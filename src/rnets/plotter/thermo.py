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
    , cfg: GraphCfg = GraphCfg()
) -> Graph:
    """Build a dotgraph from a reaction network.

        nw (:obj:`Network`): Network object to be converted into dot graph.
        cfg (:obj:`GraphCfg`, optional): Graphviz configuration.

    Returns:
        Dot :obj:`Graph` with the colors and shapes of the netwkork.
    """
    c_norm: Callable[[float], Color] = color_interp(
        norm_fn=network_energy_normalizer(nw)
        , cs=cfg.colorscheme
        , offset=cfg.color_offset
    )
    n_color_fn: Callable[[float, Visibility], tuple
                         [Color, Color]] = nodecolor_sel(
        c_norm=c_norm
        , fg_c=cfg.node.font_color
        , fg_alt=cfg.node.font_color_alt
        , lum_threshold=cfg.node.font_lum_threshold
    )
    e_widths: Iterator[float]
    if cfg.edge.max_width is None:
        e_widths = repeat(cfg.edge.width)
    else:
        e_widths = calc_reactions_k_norms(
            rs=nw.reactions
            , norm_range=(cfg.edge.width, cfg.edge.max_width)
          )
    e_colors: Iterator[Color]
    if cfg.edge.solid_color is None:
        e_colors = map(lambda r: c_norm(r.energy), nw.reactions)
    else:
        e_colors = repeat(cfg.edge.solid_color)

    return Graph(
        kind=cfg.kind
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
        , options=build_glob_opt(cfg)
    )
