"Module containing the plotter for the reaction networks testing"

from collections.abc import Callable, Iterable, Iterator, Sequence
from enum import StrEnum
from math import exp
from functools import partial, reduce
from itertools import chain, repeat, product, starmap
from typing import NamedTuple

from .dot import Edge, Graph, Node, Opts, OptsGlob
from .struct import Compound, FFlags, Network, Reaction
from .colors.utils import (
    Color
    , color_sel_lum
    , interp_fn_rgb_hls
    , rgb_to_hexstr
)
from .colors.colorschemes import INFERNO, VIRIDIS, PLASMA, MAGMA, CIVIDIS


DEF_T: float = 273.15
C_WHITE: Color = (1., 1., 1.)
C_BLACK: Color = (0., 0., 0.)
COLORSCH: Sequence[Color] = VIRIDIS

GRAPH_ATTR_DEF: Opts = {
    'rankdir': 'TB'
    , 'ranksep': '0.5'
    , 'nodesep': '0.25'
}
NODE_ATTR_DEF: Opts = {
    "shape": "plaintext"
    , "style": "filled"
}
BOX_TMP: str = """<
<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0">
  <TR>
    <TD>{0}</TD>
  </TR>
</TABLE>
>
"""
LABEL_TMP: str = '<FONT COLOR="{0}">{1}</FONT>'


class HTMLFormat(StrEnum):
    """HTML format for strings.
    """
    Bold = "<b>{}</b>"
    Italic = "<i>{}</i>"
    Underscore = "<u>{}</u>"


class NodeCfg(NamedTuple):
    """Dot node general configuration.

    Attributes:
        opts (dict of str as keys and str as values or None, optional): Dot
            additional global node options. Defauts to None.
        box_tmp (str, optional): Box template. Should have two format
            modificators, the first consisting on the label and the second
            consisting on the background color. Defaults to :obj:`BOX_TMP`
        font_color (:obj:`Color`, optional): Font color of the node. Defaults
            to :obj:`C_BLACK`
        font_color_alt (:obj:`Color` or None, optional): Alternative font
            color. If not None, would be used as the font color for dark background
            colors (see :obj:`calc_relative_luminance`)
        font_lum_threshold (float on None, optional): If :attr:`font_color_alt`
            is defined, the luminance threshold to use it instead of
            :attr:`font_color`.
    """
    opts: Opts | None = NODE_ATTR_DEF
    box_tmp: str = BOX_TMP
    font_color: Color = C_BLACK
    font_color_alt: Color | None = C_WHITE
    font_lum_threshold: float | None = None


class EdgeCfg(NamedTuple):
    """Dot edge general configuration.

    Attributes:
        opts (dict of str as keys and str as values or None, optional): Dot
            additional global edge options. Defauts to None.
        solid_color (:obj:`Color` or None, optional): If set, all lines will be
            draw with that color, else, the color will be decided based on the
            reaction energy. Defaults to None.
        width (float, optional): Minimum width of the edges. Defaults to 1..
        max_width (float or None, optional): If set, the width or the arrows
            will be decided based on their kinetic constant (k, see
            :obj:`calc_pseudo_k_constant`), using width as the minimum width
            and this max_width as the maximum width, if None, all the arrows
            will be draw with constant width.
        temperature (float, optional): Temperature to compute the kinetic
            constants. Defaults to :obj:`DEF_T`.
    """
    opts: Opts | None = None
    solid_color: Color | None = None
    width: float = 1
    max_width: float | None = 5
    temperature: float = DEF_T


class GraphCfg(NamedTuple):
    """Dot graph general configuration.

    Attributes:
        opts (dict of str as keys and str as values or None, optional): Dot
            additional global graph options. Defauts to None. Defaults to
            :obj:`GRAPH_ATTR_DEF`.
        kind (str, optional): Kind of the dotgraph. Defaults to digraph.
        colorscheme (sequence of floats): Sequence of colors that will be
           interpolate to set the colors of the graph. See
           :obj:`interp_fn_rgb_hls`. Defaults to :obj:`COLORSCH`.
        color_offset (tuple of two floats, optional): When using the energy of
            a node to decide its color, the offset to apply to norm. Should be
            a value between 0. and 1. Useful to avoid falling on the extremes
            of a predefined colorscheme. Defaults to (0., 0.)
    """
    opts: Opts | None = GRAPH_ATTR_DEF
    kind: str = "digraph"
    colorscheme: Sequence[Color] = COLORSCH
    color_offset: tuple[float, float] = (0., 0.)
    node: NodeCfg = NodeCfg()
    edge: EdgeCfg = EdgeCfg()


def calc_activation_energy(
    r: Reaction
) -> float:
    """Computes the activation energy of a given compounds

    Args:
        r (:obj:`Reaction`): Reaction that will be used to calculate the Ea.

    Returns:
        float: Activation energy.

    Note:
        Note that the units are not checked. The energy of the :obj:`Reaction`
            and its attached compounds should be in the same units.
    """
    return r.energy - (sum(map(lambda x: x.energy, r.compounds[0])))


def calc_pseudo_k_constant(
    ea: float
    , T: float = DEF_T
) -> float:
    """Computes a pseudo equilibrium constant (k) for the given activation
    energy. This constant serves a proxy to visually compare reaction kinetics.

    Args:
        ea (float): Reaction energy.
        T (float): Temperature at which the kinetic constant is
            computed. Defaults to :obj:`DEF_T`.

    Returns:
       float: Computed pseudo-k.

    Notes:
        Use :obj:`calc_activation_energy` to compute the energy for a give
        :obj:`Reaction` object.

       Units are not taken into account. Make sure that the temperature and
       energy units match.
    """
    return exp(ea / T)


def calc_reactions_k_norms(
    rs: Sequence[Reaction]
    , T: float = DEF_T
    , norm_range: tuple[float, float] = (0., 1.)
) -> Iterator[float]:
    """From a set of reactions, compute the norm of each reaction using the
    pseudo kinetic constant (see :obj:`calc_pseudo_kconstant`).

    Args:
        rs (sequence of :obj:`Reaction`): Reactions to use to compute the norm.
        T (float): Temperature at which the kinetic constant is
            computed. Defaults to :obj:`DEF_T`.

    Returns:
        :obj:`Iterator` of float: Computed k norms preserving the order of the
            given reactions.
    """
    ks: tuple[float, ...] = tuple(map(
        lambda r: calc_pseudo_k_constant(calc_activation_energy(r), T)
        , rs
    ))
    norm: Callable[[float], float] = normalizer(*minmax(ks))
    n_ran: float = norm_range[1] - norm_range[0]

    return map(lambda x: (norm(x) * n_ran) + norm_range[0], ks)


def normalizer(
    s: float
    , e: float
) -> Callable[[float], float]:
    """Creates a normalization function that returns a value between 0 and
    1 depending on the minimum and maximum values.

    Args:
        s (float): Starting (mininum) value used for the normalization.
        e (float): Ending (maximum) value used for the normalization.

    Returns:
        Callable[[float], float]: Function that normalizes a float within the
            normalization range.

    Note:
        If the normalization function overflows, it will return 0 in case of
            values smaller than the minimum or 1 in case of values higher than
            the ending value.
    """
    rang: float = e - s

    def norm(
        x: float
    ) -> float:
        if x < s:
            return 0.
        if x > e:
            return 1.
        return (x - s) / rang

    return norm


def minmax(
    xs: Iterable[float]
) -> tuple[float, float]:
    """Simple function that returns the minimum and the maximum of a sequence
    of floats.

    Args:
        xs (sequence of float): Sequence to examine.

    Return:
        tuple of two floats: With the form of (min, max).

    Notes:
        I tried to make this function from scratch, but it seems that the
            implementation of min and max are extremely efficient; it is better
             to create two maps and then search for the min and max.
    """
    ys: tuple[float, ...] = tuple(xs)
    return (min(ys), max(ys))


def network_energy_normalizer(
    n: Network
) -> Callable[[float], float]:
    """Given a reaction network, build an energy normalizer based on the
    maximum energies of the compounds and reactions.

    Args:
        n (:obj:`Network`): Network for which the normalizer will be built.

    Returns:
        Callable[[float], float]: Function that normalizes a float using
        minimum and maximum values of the network and an offset
    """
    return normalizer(*minmax(chain.from_iterable(map(
        lambda xs: starmap(
            getattr
            , zip(xs, repeat("energy")
        ))
        , (n.compounds, n.reactions)
    ))))


def network_color_interp(
    n: Network
    , cs: Sequence[Color]
    , offset: tuple[float, float] = (0., 0.)
) -> Callable[[float], Color]:
    """Given a reaction network and a sequence of colors, build a color
    interpolation function that converts the energy of a component inside the
    network to the corresponding color in the color sequence.

    Args:
        n (:obj:`Network`): Reaction network.
        cs (sequence of :obj:`Color`): Sequence of colors to interpolate.
        offset (tuple of 2 float, optional): Minimum and maximum energy offsets
            to add to the minimum and maximum detected energies.

    Returns:
        Callable[[float], :obj:`Color`]: A function that takes a float as input
            an returns a :obj:`Color` as output.

    Notes:
        The normalizer is set for the input network and thus, if an energy
            value that it is out of range is used as input, the normalization
            will follow the (under)overflow rules of :obj:`normalizer`.

        I found that the offset is extremely useful to avoid very dark and very
            bright zones of certain colorschemes.
    """
    c_interp: Callable[[float], Color] = interp_fn_rgb_hls(cs)
    e_rng: Callable[[float], float] = network_energy_normalizer(n)

    def interp_fn(x: float) -> Color:
        return c_interp(e_rng(x))

    return interp_fn


def fformat_to_html(
    f: FFlags
) -> HTMLFormat:
    """Convert :obj:`FFlags` to :obj:`HTMLFormat`.

    Args:
        f (:obj:`FFlags`): FFlags to convert.

    Returns:
       :obj:`HTMLFormat`: HTML format conversion.
    """
    match f:
        case FFlags.I: return HTMLFormat.Italic
        case FFlags.B: return HTMLFormat.Bold
        case FFlags.U: return HTMLFormat.Underscore


def apply_html_format(
    s: str
    , fs: set[FFlags]
) -> str:
    """Given a set of :obj:`FFlags` apply it as HTML format labels to a string.

    Args:
        s (str): String to apply the format.
        fs (set of :obj:`FFlags`): Set with the formats to apply.

    Returns:
        str: with the applied HTML formats.
    """
    return reduce(
        lambda x, f: fformat_to_html(f).format(x)
        , fs
        , s
    )


def build_node_box(
    s: str
    , fc: Color = C_BLACK
    , box_tmp: str = BOX_TMP
) -> str:
    """Creates an string describing a colored-background HTML with a text label
    in the middle. This is the typical node representation of this code.

    Args:
        s (str): String that will be used as a label.
        fc (:obj:`Color`, optional): Text color for the label. Defaults to black
             (:obj:`C_BLACK`).
        box_tmp (str, optional): Box template. Should have a format modificator
            for the text label. Defaults to :obj:`BOX_TMP`
    Returns:
        str: HTML table with the given label, background color and text color.

    Note:
        Note that :obj:`Color` follows the colorsys representation, meaning
            that it consists of 3 float values ranging from [0, 1].
    """
    return box_tmp.format(
        LABEL_TMP.format(
            rgb_to_hexstr(fc), s
        ))


def gen_react_arrows(
    rt: Sequence[Compound]
    , pt: Sequence[Compound]
) -> Iterator[tuple[Compound, Compound]]:
    """Given a set of reactants and a set of products, generate an iterator
    that returns every react->product combination, skipping the ones containing
    a not visible :obj:`Compound`.

    Args:
        rt (sequence of :obj:`Compound`): Compounds acting as reactants.
        pt (sequence of :obj:`compound`): Compounds acting as products.

    Returns:
        :obj:Iterator[tuple[:obj:`Compound`, :obj:`Compound`]]: A consumable
            iterator with all the (react, product) combinations excluding
            the ones with non visible compounds.
    """
    filter_vis = partial(filter, lambda x: x.visible)
    return product(filter_vis(rt), filter_vis(pt))


def build_dotnode(
    c: Compound
    , bc: Color = C_WHITE
    , fc: Color = C_BLACK
) -> Node:
    """Creates a :obj:`Node` from a :obj:`Compound`.

    Args:
        c (:obj:`Compound`): Compound to be coverted.
        bc (:obj:`Color`, optional): RGB color of the background. Defaults to
            white.
        fc (:obj:`Color`, optional): RGB color of the text. Defaults to black
            (:obj:`C_BLACK`).

    Returns:
        :obj:`Node`: Dot node with the given font and background colors.
            Inherits applies the format flags and the dot opts in
           :obj:`Compound`.

    Note:
        To allow custom labels, this function will check for "label" in
            :attr:`Compound.opts`, if found, it will use it instead of the
            layer.
    """
    l: str = c.opts["label"] if (c.opts and "label" in c.opts) else c.name
    return Node(
        name=l
        , options=c.opts or {} | {
            "label": build_node_box(
                s=apply_html_format(l, c.fflags) if c.fflags else l
                , fc=fc
            )
            , "fillcolor": '"{}"'.format(rgb_to_hexstr(
                c=bc
                , inc_hash=True
            ))
        }
    )


def build_dotedges(
    r: Reaction
    , width: float
    , color: Color = C_BLACK
) -> Iterator[Edge]:
    """Converts a `Reaction` into one or more dot :obj:`Edge`.

    Args:
        r (:obj:`Reaction`): Reaction to convert.
        width (float): Width of the reaction arrow.
        color (:obj:`Color`, optional): Color of the arrow. Defaults to
            :obj:`C_BLACK`.

    Returns:
        :obj:`Iterator`[:obj:`Edge`]: Iterator with the generated dot
            :obj:`Edge` corresponding to the :obj:`Reaction` with the given
            width and color.
    """
    def build_edge(o: str, t: str) -> Edge:
        return Edge(
            origin=o
            , target=t
            , direction="->"
            , options=r.opts or {} | {
                "color": f'"{rgb_to_hexstr(color, inc_hash=True)}"'
                , "penwidth": str(width)
            }
        )

    return starmap(build_edge, gen_react_arrows(*r.compounds))


def nodecolor_sel(
    c_norm: Callable[[float], Color]
    , fg_c: Color = C_BLACK
    , fg_alt: Color | None = None
    , lum_threshold: float | None = None
) -> Callable[[Compound], tuple[Color, Color]]:
    """Creates a function that takes an energy as input and returns the
    assigned color for the background of the node and the foreground.

    Args:
        c_norm (Function taking a float as input and returns a :obj:`Color`):
            Color normalizer that will be used to compute the color of the
            node background. See :obj:`network_color_interp`.
        fg_c (:obj:`Color`, optional): Color of the text. Defaults to
            :obj:`C_BLACK`.
        fg_alt (:obj:`Color`, optional): If set, alternative :obj:`Color` for
            the text if the luminance is below the a certain
            threshold. Defaults to None.
        lum_threshold (float, optional): If set, threshold of the luminance. If
            None, the default value in :obj:`color_sel_lum` will be used. This
            argument has no effect if :attr:`fg_alt` is not defined. Ideally,
            a value between 0. and 1. Defaults to None.

    Returns:
        :obj`Callable`[[:obj:`Compound`], tuple[:obj:`Color`, :obj:`Color`]:
            A function that given a :obj:`Compound` returns a tuple of two
            :obj:`Color`s, the first being the background color and the second
            one being the color of the font.
    """
    if fg_alt:
        def fg_fn(x: Color) -> Color:
            return color_sel_lum(fg_c, fg_alt, x, lum_threshold or 0.5)
    else:
        def fg_fn(x: Color) -> Color: return fg_c

    def out_fn(x: Compound) -> tuple[Color, Color]:
        bg_c: Color = c_norm(x.energy)
        return (bg_c, fg_fn(bg_c))

    return out_fn


def build_glob_opt(
    cfg: GraphCfg
) -> OptsGlob | None:
    """Given a certain :obj:`GraphCfg`, build a dictionary containing the dot
    options for the graph, the node and the edges.

    Args:
        cfg (:obj:`GraphCfg`): Configuration to use to generate the dictionary.

    Returns:
        :obj:`OptsGlob`: With the given dictionary. Using graph, node and edge
            as keys and their corresponding :obj:`Opts` as values.
        None: If no Opts are found.
    """
    # After dealing with the type checker, this is the less problematic
    # solution to convince it that there are no None values in the dictionary.
    nms: tuple[str, ...] = ("graph", "node", "edge")
    os: tuple[Opts | None, ...] = (cfg.opts, cfg.node.opts, cfg.edge.opts)

    return {k: v for k, v in zip(nms, os) if v is not None} or None


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
    c_norm: Callable[[float], Color] = network_color_interp(
        n=nw
        , cs=cfg.colorscheme
        , offset=cfg.color_offset
    )
    n_color_fn: Callable[[Compound], tuple
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
            , T=cfg.edge.temperature
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
            lambda c: build_dotnode(c, *n_color_fn(c))
            , filter(lambda c: c.visible, nw.compounds)
        ))
        , edges=tuple(chain.from_iterable(starmap(
            build_dotedges
            , filter(
                lambda xs: tuple(xs)[0].visible  # Tuple for __getitem__
                , zip(nw.reactions, e_widths, e_colors)
            )
        )))
        , options=build_glob_opt(cfg)
    )
