# -*- coding: utf-8 -*-
from collections import Counter
from collections.abc import Callable, Iterable, Iterator, Sequence
from functools import reduce
from math import exp
from itertools import chain, repeat, starmap
from typing import NamedTuple

from .struct import Compound, Network, Reaction

CONSTANTS = {
    "kb": {
        "eV": 8.62E-5
        , "kj/mol": 1.38E-23
        , "kcal/mol": 1.99E-3
    }
    , "h": {
        "eV": 4.14E-15
        , "kj/mol": 3.99E-3
        , "kcal/mol": 9.55E-14
    }
}

DEF_T: float = 273.15                  # Standard temperature in K
DEF_A: float = 1E13                    # Arrhenius pre-exponential factor
DEF_KB: float = CONSTANTS["kb"]["eV"]  # Boltzmann constat eV and K


class ChemCfg(NamedTuple):
    """Chemical system general configuration.

    Attributes:
        T (float): Temperature of the chemical system in Kelvin. Defaults to
            the standard temperature (:obj:`DEF_T`.).
        e_units (str): Energy units. Defaults to "eV"
        kb: (float): Boltzmann constat. Defaults to eV and K (:obj:`DEF_KB`)
        A: (float): Arrhenius pre-exponential factor. Defaults to 1 (:obj:`DEF_A`).
    """
    T: float = DEF_T
    e_units: str = "eV"
    kb: float = DEF_KB
    A: float = DEF_A


def build_chemcfg(
    T: float
    , e_units: str = "eV"
    , kb: float | None = None
    , h: float | None = None
    , A: float | None = None
) -> ChemCfg:
    """Wrapper to build a ChemCfg taking into account pre-known constant values.

    Attributes:
        T (float): Temperature of the chemical system in Kelvin. Defaults to
            the standard temperature (:obj:`DEF_T`.).
        e_units (str, optional): Energy units. Defaults to "eV".
        kb: (float): Boltzmann constat. If None, its value will be search at
            :obj:`CONSTANTS`. If the constant is not found, a
            :obj:`NotImplementedError` will be raised.
        h (float): Planck constat. In case :obj:`h` and :obj:`A` are None, its
            value will be search at :obj:`CONSTANTS` based on the provided
            units. If the constant is not found, a :obj:`NotImplementedError`
            will be raised. Defaults to None
        A: (float): Arrhenius pre-exponential factor. If not provided, it
            will be computed with kb and h.

    Returns:
        :obj:`ChemCfg` with the given configuration.

    Raises:
            for the given units (:obj:`e_units`)
    """
    if kb is None:
        if CONSTANTS["kb"].get(e_units) is None:
            raise NotImplementedError("kb not implemented for {e_units}")
        kb_var: float = CONSTANTS["kb"][e_units]
    else:
        kb_var: float = kb
    if A is None:
        if h is None and e_units not in CONSTANTS["h"]:
            raise NotImplementedError("h not implemented for {e_units}")
        A_var: float = calc_A(T, kb_var, CONSTANTS["h"][e_units])
    else:
        A_var: float = A
    return ChemCfg(
        T=T
        , e_units=e_units
        , kb=kb_var
        , A=A_var
    )


def calc_A(
    T: float
    , kb: float
    , h: float
) -> float:
    """Given a temperature, a boltzmann constant and the planck constant,
    compute the Arrhenius pre-exponential factor.

    Args:
        T (float): Temperature.
        kb (float): Boltzmann constant.
        h (float): Planck constant.

    Returns:
        Arrhenius pre-exponential factor as float.
    """
    return (kb * T / h)


def calc_activation_energy(
    r: Reaction
    , reverse: bool = False
) -> float:
    """Computes the activation energy of a given compounds

    Args:
        r (:obj:`Reaction`): Reaction that will be used to calculate the Ea.
        inv (bool, optional): Compute the energy of the reverse
            reaction. Defaults to False

    Returns:
        float: Activation energy.

    Note:
        Note that the units are not checked. The energy of the :obj:`Reaction`
            and its attached compounds should be in the same units.
    """
    return r.energy - (sum(map(lambda x: x.energy, r.compounds[int(reverse)])))


def calc_pseudo_k_constant(
    ea: float
    , T: float
    , A: float = DEF_A
    , kb: float = DEF_KB
) -> float:
    """Uses the arrhenious equation to compute a pseudo equilibrium constant
    (k) for the given activation energy. This constant serves a proxy to
    visually compare reaction kinetics.

    Args:
        ea (float): Reaction energy.
        T (float): Temperature at which the kinetic constant is
            computed. Defaults to :obj:`DEF_T`.
        A (float): Pre-exponential factor for the Arrhenious equation. Defaults
            to :obj:`DEF_T`.
        kb (float): Boltzmann constant. Defaults to :obj:`DEF_KB`

    Returns:
       float: Computed pseudo-k.

    Notes:
        Use :obj:`calc_activation_energy` to compute the energy for a give
        :obj:`Reaction` object.

       Units are not taken into account. Make sure that the temperature and
       energy units match.
    """
    return A*exp((-ea/(kb*T)))


def calc_net_rate(
    r: Reaction
    , T: float
    , A: float
    , kb: float
) -> float | None:
    """Given a reaction, a temperature, and pre-exponential factor,
    computer the net rate constant.

    Args:
        T (float): Temperature of the reaction.
        A (float): Pre-exponential factor used in the Arrhenius equation.
        kb (float): Boltzmann constant.

    Note:
        Note that the units are not checked. The user should provide the
        arguments with matching units.
    """
    ccomp = tuple(map(Counter, r.compounds))

    # Check if the reaction is an elementary
    if not all(map(lambda x: 0 < len(x) <= 2, ccomp)): return None

    rr = tuple(map(
        lambda c: tuple(starmap(
            lambda k, v: None if k.conc is None else k.conc**v
            , c.items()))
        , ccomp))


    # Check for missing concentrations
    if None in chain.from_iterable(rr): return None

    ks = map(
            lambda b: calc_pseudo_k_constant(
                calc_activation_energy(r, reverse=b)
                , T, A, kb)
            , (False, True))

    return sum(starmap(
        lambda r, k: reduce(lambda x, y: x*y, (k,) + r, 1)
        , zip(rr, ks)
    ))


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
    minimum and maximum energies of the compounds and reactions.

    Args:
        n (:obj:`Network`): Network for which the normalizer will be built.

    Returns:
        Callable[[float], float]: Function that normalizes a given float using
        minimum and maximum values of the network and an offset.
    """
    return normalizer(*minmax(chain.from_iterable(map(
        lambda xs: starmap(
            getattr
            , zip(xs, repeat("energy")
        ))
        , (n.compounds, n.reactions)
    ))))


def network_conc_normalizer(
    nw: Network
) -> Callable[[float], float]:
    """Given a reaction network, build a concentration normalizer based on the
    maximum and minimum concentration of the compounds in the network.

    Args:
        nw (:obj:`Network`): Network for which the normalizer will be built.

    Returns:
        Callable[[float], float]: Function that normalizes a float using
        minimum and maximum values of the network and an offset
    """
    def f_none(xs: Sequence[float | None]) -> Iterator[float]:
        return filter(lambda x: x is not None, xs)

    return normalizer(*minmax(starmap(
            getattr
            , zip(f_none(nw.compounds), repeat("conc")))))
