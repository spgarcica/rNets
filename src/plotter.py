"Module containing the plotter for the reaction networks testing"

from functools import reduce
from math import copysign, exp
from itertools import chain, repeat, starmap
from typing import Callable, Iterator, Sequence, Tuple

from .dot import Edge, Graph, Node
from .struct import Compound, Reaction, Network


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
    r: Reaction
    , rev: bool = False
) -> float:
    """Computes the activation energy of a given reaction.

    Args:
        r (`Reaction`): Reaction for which the energy will be computed.
        rev (bool, optional): If True, the energy of the reaction will be
            computed right to left. Defaults to False.

    Returns:
        Activation energy as a float.

    Notes:
        Note that the units are not checked. The energy of `Reaction` and their
        `Compound`s should be be in the same units.
    """
    es: Tuple[float, float] = tuple(map(
        lambda cs: sum(map(
            lambda c: c.energy
            , cs
        ))
        , r.compounds
    ))

    # Sign function not available in Python, using copysign.
    return (es[1] - es[0]) * copysign(1, (rev * -1))


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


def network_energy_minmax(
    n: Network
    , offset: Tuple[float, float] | None = None
) -> Callable[float, float]:
    """Given a reaction network, build an energy normalizer based on the
    maximum energies of the compounds and reactions.

    Args:
        n (`Network`): Network for which the normalizer will be built.
        offset (tuple of 2 floats, optional): If provided, apply an offset to
            the minimum and maximum energy values on the network.

    Returns:
        Normalization function of the form f :: float -> float using minimum
        and maximum values of the network and the offset as the maximum values.
    """
    if not offset:
        offset = (0, 0)
    s, e = minmax(chain.from_iterable(map(
        lambda xs: starmap(
            getattr
            , zip(xs, repeat("energy")
        ))
        , (n.compounds, n.reactions)
    )))
    return (s + offset[0], e + offset[1])


def build_node_box(
    s: str
    ,
)


def compound_to_dotnode(
    c: Compound
) -> Node:
    """Creates a `Node` from a `Compound`.

    Args:
        c (`Compound`): Compound to convert.

    Returns:
        Dot `Node`.
    """
    Node(
        name=c.name
        , options={
            "label":
        }
