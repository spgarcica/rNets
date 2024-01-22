from collections.abc import Sequence
from itertools import chain, repeat, starmap
from functools import partial, reduce
from typing import Callable, Iterator

from ..colors import Color
from ..chemistry import (
    calc_net_rate
    , normalizer
    , minmax
    , ChemCfg
    , network_conc_normalizer
)
from ..dot import Graph
from ..struct import Compound, Reaction, Network, Visibility

from .utils import (
    EdgeArgs
    , build_glob_opt
    , build_dotnode
    , build_dotedges
    , nodecolor_sel
    , color_interp
    , GraphCfg
)


def filter_unique_react(
    rs: Sequence[Reaction]
) -> tuple[Reaction, ...]:
    """Given a set of reactions that may contain biderectional reactions,
    return a set without the reversed reactions.
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
) -> Graph:
    """Build a dotgraph from a reaction network.

        nw (:obj:`Network`): Network object to be converted into dot graph.
        cfg (:obj:`GraphCfg`, optional): Graphviz configuration.

    Returns:
        Dot :obj:`Graph` with the colors and shapes of the netwkork.
    """
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
        e_dir = repeat(False)
    else:
        rates: tuple(float, ...) = tuple(map(
            partial(calc_net_rate, T=chem_cfg.T, A=chem_cfg.A, kb=chem_cfg.kb)
            , u_react))
        e_widths: Iterator[float] = map(
            normalizer(*minmax(map(abs, rates)))
            , rates)
        e_dir = map(lambda x: x < 0, rates)

    return Graph(
        kind=graph_cfg.kind
        , nodes=tuple(map(
            lambda c: build_dotnode(c, *n_color_fn(c.conc, c.visible))
            , filter(lambda c: c.visible != Visibility.FALSE, nw.compounds)
        ))
        , edges=tuple(chain.from_iterable(starmap(
            build_dotedges
            , filter(
                # Tuple for __getitem__
                lambda xs: EdgeArgs(*xs).react.visible != Visibility.FALSE
                , zip(u_react, e_widths, e_colors, e_dir)
            )
        )))
        , options=build_glob_opt(graph_cfg)
    )
