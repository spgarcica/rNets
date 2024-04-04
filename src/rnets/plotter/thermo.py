"""Thermodynamic plot module. Given the energies of the compounds
and the transition states, this module creates a graph summarizing the
thermodynamic/kinetic behavior of the system. The background of the nodes and
the fill color of the edges is set depending on their energies, while the width
of the edges is based on their computed kinetic constants.
"""
from itertools import chain, repeat, starmap
from typing import Callable, Iterator

from ..colors import Color
from ..chemistry import (
    network_energy_normalizer
    , calc_reactions_k_norms
    , ChemCfg
)
from ..dot import Graph
from ..struct import Network, Visibility

from .utils import (
    EdgeArgs
    , build_glob_opt
    , build_dotnode
    , build_dotedges
    , nodecolor_sel
    , color_interp
    , GraphCfg
)


def build_dotgraph(
    nw: Network
    , graph_cfg: GraphCfg = GraphCfg()
    , chem_cfg: ChemCfg = ChemCfg()
) -> Graph:
    """Build a dotgraph from a reaction network.

        nw (:obj:`Network`): Network object to be converted into dot graph.
        graph_cfg (:obj:`GraphCfg`, optional): Graphviz configuration. Defaults
            to :obj:`ChemCfg`
        chem_cfg (:obj:`ChemCfg`, optional): Chemical parameters fo the
            system. Defaults to :obj:`ChemCfg`

    Returns:
        Dot :obj:`Graph` with the colors and shapes of the netwkork.
    """
    c_norm: Callable[[float], Color] = color_interp(
        norm_fn=network_energy_normalizer(nw)
        , cs=graph_cfg.colorscheme
        , offset=graph_cfg.color_offset
    )
    n_color_fn: Callable[[float, Visibility], tuple
                         [Color, Color]] = nodecolor_sel(
        c_norm=c_norm
        , fg_c=graph_cfg.node.font_color
        , fg_alt=graph_cfg.node.font_color_alt
        , lum_threshold=graph_cfg.node.font_lum_threshold
    )
    e_widths: Iterator[float]
    if graph_cfg.edge.max_width is None:
        e_widths = repeat(graph_cfg.edge.width)
    else:
        e_widths = calc_reactions_k_norms(
            rs=nw.reactions
            , T=chem_cfg.T
            , A=chem_cfg.A
            , kb=chem_cfg.kb
            , norm_range=(graph_cfg.edge.width, graph_cfg.edge.max_width)
          )
    e_colors: Iterator[Color]
    if graph_cfg.edge.solid_color is None:
        e_colors = map(lambda r: c_norm(r.energy), nw.reactions)
    else:
        e_colors = repeat(graph_cfg.edge.solid_color)

    return Graph(
        kind=graph_cfg.kind
        , nodes=tuple(map(
            lambda c: build_dotnode(c, *n_color_fn(c.energy, c.visible))
            , filter(lambda c: c.visible != Visibility.FALSE, nw.compounds)
        ))
        , edges=tuple(chain.from_iterable(starmap(
            build_dotedges
            , filter(
                # Tuple for __getitem__
                lambda xs: EdgeArgs(*xs).react.visible != Visibility.FALSE
                , zip(nw.reactions, e_widths, e_colors)
            )
        )))
        , options=build_glob_opt(graph_cfg)
    )
