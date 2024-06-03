"""Kinetic plot module. Given the energies and concentrations of the compounds
and the energies transition states, this module creates a graph summarizing the
kinetic behavior of the system. The background of the nodes is colored
depending on their concentration, while the width of the edges and the
direction of the arrows is decided based on the calculated net rate.
"""
from collections.abc import Sequence
from itertools import chain, repeat, starmap
from functools import partial, reduce
from typing import Callable, Iterator, Iterable

from ..colors.utils import Color, ColorSpace, interp_cs
from ..chemistry import (
    calc_net_rate
    , normalizer
    , minmax
    , ChemCfg
    , network_conc_normalizer
)
from ..addons.colorbar import build_colorbar, build_anchor, ColorbarCfg
from ..dot import Edge, Graph, Node
from ..struct import Reaction, Network, Visibility

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
    , colorbar_cfg: ColorbarCfg
    , colorspace: ColorSpace="lab"
) -> tuple[Node, Edge | tuple[()]]:
    """Build a colorbar for the thermodynamic plot.

    Args:
        graph_cfg (:obj:`GraphCfg`, optional): Graphviz configuration. Defaults
            to :obj:`ChemCfg`.
        colorbar_cfg (:obj:`ColorbarCfg` or None, optional): Colorbar
            parameters of the system. Defaults to None.
        colorspace (ColorSpace, optional): Colorspace of the colorbar. Defaults
            to "lab".

    Returns:
        tuple of two values, the first one being a obj:`Node` representing the
        color bar and the second value being an invisible edge that anchors the
        colorbar to another node.
    """
    def f_none[T](xs: Iterable[T | None]) -> Iterable[T]:
        return (x for x in xs if x is not None)
    c_range = minmax(starmap(
            getattr
            , zip(f_none(nw.compounds), repeat("conc"))))
    anchor: Edge | tuple[()] = ()
    if colorbar_cfg.anchor is not None:
        anchor = build_anchor(colorbar_cfg.anchor, colorbar_cfg.node_name)
    return (
        build_colorbar(
            interp_cs(graph_cfg.colorscheme, colorspace)
            , c_range
            , colorbar_cfg
            , "Concentration")
        , anchor)


def filter_unique_react(
    rs: Sequence[Reaction]
) -> tuple[Reaction, ...]:
    """Given a set of reactions that may contain biderectional reactions,
    return a set without the reversed reactions.

    Args:
        rs (sequence of :obj:`Reaction`): Sequence of reactions that will bee
           filtered.

    Returns:
        Tuple containing the unique :obj:`Reaction` s.
    """
    def r_fn(xs: tuple[Reaction, ...], x: Reaction) -> tuple[Reaction, ...]:
        cmp_hash: int = hash(tuple(reversed(x.compounds)))
        fn_check = lambda y: hash(y.compounds) == cmp_hash
        return xs if any(map(fn_check, xs)) else xs + (x,)

    return reduce(r_fn, rs, ())


def build_dotgraph(
    nw: Network
    , graph_cfg: GraphCfg = GraphCfg()
    , chem_cfg: ChemCfg = ChemCfg()
    , colorbar_cfg: ColorbarCfg | None = None
) -> Graph:
    """Build a kinetic dotgraph from a reaction network.

    Args:
        nw (:obj:`Network`): Network object to be converted into dot graph.
        graph_cfg (:obj:`GraphCfg`, optional): Graphviz configuration. Defaults
            to :obj:`ChemCfg`
        chem_cfg (:obj:`ChemCfg`, optional): Chemical parameters fo the
            system. Defaults to :obj:`ChemCfg`
        colorbar_cfg (:obj:`ColorbarCfg` or None, optional): Colorbar
            parameters of the system. Defaults to None.

    Returns:
        Dot :obj:`Graph` representing the kinetic information with the colors
        and shapes of the network.
    """
    if colorbar_cfg is None:
        cb_node, cb_edge = ((),())
    else:
        cb_node, cb_edge = get_colorbar(
            nw
            , graph_cfg
            , colorbar_cfg)
    c_norm: Callable[[float], Color] = color_interp(
        norm_fn=network_conc_normalizer(nw)
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

    u_react: tuple[Reaction, ...] = filter_unique_react(nw.reactions)
    e_colors: Iterator[Color | None] = repeat(graph_cfg.edge.solid_color)
    e_widths: Iterator[float]
    e_dir: Iterator[bool]
    if graph_cfg.edge.max_width is None:
        e_widths = repeat(graph_cfg.edge.width)
        # TODO: Draw it with lines
        e_dir = repeat(False)
    else:
        rates: tuple[float, ...] = tuple(map(
            partial(calc_net_rate, T=chem_cfg.T, A=chem_cfg.A, kb=chem_cfg.kb)
            , u_react))

        def e_width_aux(x: float) -> float:
            assert graph_cfg.edge.max_width is not None
            return x * (graph_cfg.edge.max_width - graph_cfg.edge.width) + graph_cfg.edge.width

        e_widths: Iterator[float] = map(
            e_width_aux
            , map(
                normalizer(*minmax(map(abs, rates)))
                , rates)
        )
        e_dir = map(lambda x: x < 0, rates)

    return Graph(
        kind=graph_cfg.kind
        , nodes=tuple(map(
            lambda c: build_dotnode(c, *n_color_fn(c.conc, c.visible))
            , filter(lambda c: c.visible != Visibility.FALSE, nw.compounds)
        )) + ((cb_node,) if cb_node else cb_node)
        , edges=tuple(chain.from_iterable(starmap(
            build_dotedges
            , filter(
                # Tuple for __getitem__
                lambda xs: EdgeArgs(*xs).react.visible != Visibility.FALSE
                , zip(u_react, e_widths, e_colors, e_dir)
            )
        ))) + ((cb_edge,) if cb_edge else cb_edge)
        , options=build_glob_opt(graph_cfg)
    )
