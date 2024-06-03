"""Thermodynamic plot module. Given the energies of the compounds
and the transition states, this module creates a graph summarizing the
thermodynamic/kinetic behavior of the system. The background of the nodes and
the fill color of the edges is set depending on their energies, while the width
of the edges is based on their computed kinetic constants.
"""
from itertools import chain, repeat, starmap
from typing import Callable, Iterator

from ..colors.utils import Color, ColorSpace, interp_cs
from ..chemistry import (
    network_energy_normalizer
    , minmax
    , calc_reactions_k_norms
    , ChemCfg
)
from ..dot import Edge, Node, Graph
from ..struct import Network, Visibility

from ..addons.colorbar import build_colorbar, build_anchor, ColorbarCfg
from .utils import (
    EdgeArgs
    , build_glob_opt
    , build_dotnode
    , build_dotedges
    , nodecolor_sel
    , color_interp
    , GraphCfg
)


def get_colorbar(
    nw: Network
    , graph_cfg: GraphCfg
    , chem_cfg: ChemCfg
    , colorbar_cfg: ColorbarCfg
    , colorspace: ColorSpace="lab"
) -> tuple[Node, Edge | tuple[()]]:
    """Build a colorbar for the thermodynamic plot.

    Args:
        graph_cfg (:obj:`GraphCfg`, optional): Graphviz configuration. Defaults
            to :obj:`ChemCfg`.
        chem_cfg (:obj:`ChemCfg`, optional): Chemical parameters fo the
            system. Defaults to :obj:`ChemCfg`.
        colorbar_cfg (:obj:`ColorbarCfg` or None, optional): Colorbar
            parameters of the system. Defaults to None.
        colorspace (ColorSpace, optional): Colorspace of the colorbar. Defaults
            to "lab".

    Returns:
        tuple of two values, the first one being a obj:`Node` representing the
        color bar and the second value being an invisible edge that anchors the
        colorbar to another node.
    """
    c_range = minmax(chain.from_iterable(map(
        lambda xs: starmap(
            getattr
            , zip(xs, repeat("energy")))
        , (nw.compounds, nw.reactions))))
    anchor: Edge | tuple[()] = ()
    if colorbar_cfg.anchor is not None:
        anchor = build_anchor(colorbar_cfg.anchor, colorbar_cfg.node_name)
    return (
        build_colorbar(
            interp_cs(graph_cfg.colorscheme, colorspace)
            , c_range
            , colorbar_cfg
            , "Energy" if chem_cfg.e_units is None else f"Energy ({chem_cfg.e_units})")
        , anchor)


def build_dotgraph(
    nw: Network
    , graph_cfg: GraphCfg = GraphCfg()
    , chem_cfg: ChemCfg = ChemCfg()
    , colorbar_cfg: ColorbarCfg | None = None
) -> Graph:
    """Build a dotgraph from a reaction network.
    
    Args:

        nw (:obj:`Network`): Network object to be converted into dot graph.
        graph_cfg (:obj:`GraphCfg`, optional): Graphviz configuration. Defaults
            to :obj:`ChemCfg`
        chem_cfg (:obj:`ChemCfg`, optional): Chemical parameters fo the
            system. Defaults to :obj:`ChemCfg`
        colorbar_cfg (:obj:`ColorbarCfg` or None, optional): Colorbar
            parameters of the system. Defaults to None.

    Returns:
        Dot :obj:`Graph` with the colors and shapes of the netwkork.
    """
    if colorbar_cfg is None:
        cb_node, cb_edge = ((),())
    else:
        cb_node, cb_edge = get_colorbar(
            nw
            , graph_cfg
            , chem_cfg
            , colorbar_cfg)
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
        )) + ((cb_node,) if cb_node else cb_node)
        , edges=tuple(chain.from_iterable(starmap(
            build_dotedges
            , filter(
                # Tuple for __getitem__
                lambda xs: EdgeArgs(*xs).react.visible != Visibility.FALSE
                , zip(nw.reactions, e_widths, e_colors)
            )
        ))) + ((cb_edge,) if cb_edge else cb_edge)
        , options=build_glob_opt(graph_cfg)
    )
