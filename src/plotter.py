"Module containing the plotter for the reaction networks testing"

from enum import StrEnum
from math import exp
from functools import reduce
from itertools import chain, repeat, starmap
from typing import Callable, Dict, Set, Sequence, Tuple

from .dot import Edge, Graph, Node
from .struct import Compound, FFlags, Network, Reaction
from .color import calc_relative_luminance, Color, interp_fn_rgb_hls, rgb_to_hexstr


class HTMLFormat(StrEnum):
    Bold = "<b>{}</b>"
    Italic = "<i>{}</i>"
    Underscore = "<u>{}</u>"


GRAPH_ATTR_DEF = {
    'rankdir': 'TB'
    , 'ranksep': '0.5'
    , 'nodesep': '0.5'
}

# HTML template for compound boxes
BOX_TMP: str = """<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="20">
  <TR>
    <TD BGCOLOR="{0}">{1}</TD>
  </TR>
</TABLE>
>
"""

# HTML template for the compounds text
LABEL_TMP: str = '<FONT COLOR="{0}">{1}</FONT>'


def calc_activation_energy(
    cs: Tuple[Sequence[Compound], Sequence[Compound]]
) -> float:
    """Computes the activation energy of a given compounds

    Args:
        cs (`Compounds`): Reaction for which the energy will be computed. Taking
            the compounds as the first position as the reactants and the
            products on the second position.

    Returns:
         Activation energy as a float.

    Notes:
        Note that the units are not checked. The energy of the `Compound`s
        should be be in the same units.
    """
    es: Tuple[float, float] = tuple(map(
        lambda xs: sum(map(
            lambda c: c.energy
            , xs
        ))
        , cs.compounds
    ))

    return es[1] - es[0]


def calc_pseudo_kconstant(
    ea: float
    , T: float = 273.15
) -> float:
    """Computes a pseudo equilibrium constant (k) for the given activation
    energy. This constant serves a proxy to visually compare reaction kinetics.

    Args:
        ea (float): Reaction energy.
        T (float): Temperature at which the kinetic constant is
            computed. Defaults to 273.15.

    Returns:
       Computed pseudo-k, as float.

    Notes:
        Use `calc_activation_energy` to compute the energy for a give
        `Reaction` object.

       Units are not taken into account. Make sure that the temperature and
       energy units match.
    """
    return exp(ea / T)


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
        A function with the signature fn :: float -> float that normalizes a
        float within the normalization range.

    Notes:
        If the normalization function overflows, it will return 0 in case of
        values smaller than the minimum or 1 in case of values higher than the
        ending value.
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
    xs: Sequence[float]
) -> Tuple[float, float]:
    """Simple function that returns the minimum and the maximum of a sequence
    of floats;
    Args:
        xs (sequence of float): Sequence to examine.

    Return:
        Tuple of the form (min, max).

    Notes:
        I tried to make this function from scratch, but it seems that the
        implementation of min and max are extremely efficient; it is better
        to create two maps and then search for the min and max.
    """
    ys: Tuple[float, ...] = tuple(xs)
    return (min(ys), max(ys))


def network_energy_normalizer(
    n: Network
) -> Callable[[float], float]:
    """Given a reaction network, build an energy normalizer based on the
    maximum energies of the compounds and reactions.

    Args:
        n (`Network`): Network for which the normalizer will be built.

    Returns:
        Normalization function of the form f :: float -> float using minimum
        and maximum values of the network and the offset as the maximum values.
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
    , offset: Tuple[float, float] = (0., 0.)
) -> Callable[[float], Color]:
    """Given a reaction network and a sequence of colors, build a color
    interpolation function that converts the energy of a component inside the
    network to the corresponding color in the color sequence.

    Args:
        n (`Network`): Reaction network.
        cs (sequence of `Color`): Sequence of colors to interpolate.
        offset (tuple of 2 float, optional): Minimum and maximum energy offsets
            to add to the minimum and maximum detected energies.

    Returns:
        A function that takes a float as input an returns a color as output.

    Notes:
        The normalizer is set for the input network and thus, if an energy
        value that it is out of range is used as input, the normalization will
        follow the (under)overflow rules of `normalizer`.

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
    """Convert `FFlags` to `HTMLFormat`.

    Args:
        f (`FFlags`): FFlags to convert.

    Returns:
       Converted `HTMLFormat`
    """
    match f:
        case FFlags.I: return HTMLFormat.Italic
        case FFlags.B: return HTMLFormat.Bold
        case FFlags.U: return HTMLFormat.Underscore


def apply_html_format(
    s: str
    , fs: Set[FFlags]
) -> str:
    """Given a set of `FFlags` apply it as HTML format labels to a string.

    Args:
        s (str): String to apply the format.
        fs (set of FFlags): Set with the formats to apply.

    Returns:
        str with the applied html formats.
    """
    return reduce(
        lambda x, f: fformat_to_html(f).format(x)
        , fs
        , s
    )


def build_node_box(
    s: str
    , bc: Color = (0., 0., 0.)
    , fc: Color = (1., 1., 1.)
) -> str:
    """Creates an string describing a colored-background HTML with a text label
    in the middle. This is the typical node representation of this code.

    Args:
        s (str): String that will be used as a label.
        bc (`Color`, optional): Background color for the table. Defaults to
           white ((0., 0., 0.))
        fc (`Color`, optional): Text color for the label. Defaults to black
             ((1., 1., 1.))

    Returns:
        HTML table with the given label, background color and text color.

    Notes:
        Note that `Color` follows the colorsys representation, meaning that it
        consists of 3 float values ranging from [0, 1].
    """
    return BOX_TMP.format(bc, LABEL_TMP.format(fc, s))


def build_dotnode(
    c: Compound
    , c_norm: Callable[[float], Color]
    , fc: Color = (1., 1., 1.)
    , fc_alt: Color | None = None
) -> Node:
    """Creates a `Node` from a `Compound`.

    Args:
        c (`Compound`): Compound to be coverted.
        c_norm (function): Function that takes.
        fc (`Color`, optional): RGB color of the text. Defaults to black
            (1., 1., 1.).
        fc_alt (`Color` or None, optional): If set, this color will be set for
            relative luminances lesser than 0.5. See `calc_relative_luminance`.

    Returns:
        Dot `Node` with the background color adapted for the node.

    Note:
        To allow custom labels, this function will check for "label" in
        `Compound.opts`, if found, it will use it instead of the layer.
    """
    l: str = (c.opts and c.opts.get("label")) or c.name
    if fc_alt and (calc_relative_luminance(fc_alt) < 0.5):
        fc = fc_alt
    return Node(
        name=l
        , options=c.opts | {
            "label": build_node_box(
                s=(c.fflags and apply_html_format(l, c.fflags)) or l
                , bc=rgb_to_hexstr(c_norm(c.energy))
                , fc=rgb_to_hexstr(fc)
            )
        }
    )


def build_dotedge(
    r: Reaction
    , e_norm: float
    , k_norm: float
    , max_width: float = 2.
) -> Edge:
    """Converts a reaction into one or more dot `Edge`

    Args:
        r (`Reaction`): Reaction to convert.
        e_norm (float): Normalized energy withing the range of [0., 1.].
        k_norm (function): Normalized kinetic constant within the range of [0.,
            1.].
        max_width: (float): Max arrow width. It will correspond to the maximum
            k value.
    """
    opts: Dict[str, str] = {
        "color": e_norm
        , "penwidth": k_norm * max_width
    }
    return Edge(
        start=sl
        , target=el
        , direction=direction
        , options=opts
    )


# def iter_dotedge(
#     rs: Sequence[Reaction]
#     , e_norm: Callable[[float], float]
#     , k_norm: Callable[[float], float]
# ) -> Edge:



# def network_to_dotgraph(
#     net: Network
#     , offset: Tuple[float, float] | None = None
# ) -> Graph:
#     """Given a reaction network, build a dotgraph.

#     Args:
#         net (`Network`): Network to be transformed.
#         offset (tuple of two floats, optional): Energy offset to be applied to
#             the color. Defaults to None.

#     Returns:
#         `Graph` with the nodes and edges inside the network.

#     Notes:
#         The offset should be used to change the values of the minimum and the
#         maximum energy. That will change the colors that are used to represent
#         the energies.
#     """
#     e_norm_fn: Callable[[float], float] = network_energy_minmax(net)
#     ks: [float] =
