# -*- coding: utf-8 -*-
"""Parse csv files to build compound/reaction/graph objects.

Attributes:
    S (type): Type constraint for StrEnum.
    T (type): Type variable.
    O (type): Type variable.
"""

from collections.abc import Callable, Sequence
from enum import auto, StrEnum
from functools import reduce
from itertools import chain
from pathlib import Path
from typing import TypeVar

from .struct import Compound, FFlags, Network, Reaction, Visibility

S = TypeVar('S', bound=StrEnum)
T = TypeVar('T')
O = TypeVar('O')


class CompoundCol(StrEnum):
    """Posible values for the compound columns."""
    Energy = auto()
    Name = auto()
    Visible = auto()
    Opts = auto()
    Fflags = auto()
    Conc = auto()


class Direction(StrEnum):
    """Direction of a reaction. Can be Left, Right or Bidirectional."""
    Left = "<-"
    Right = "->"
    Biderectional = "<->"


class ReactionCol(StrEnum):
    """Possible values for the reaction columns."""
    CLeft = auto()
    CRight = auto()
    Energy = auto()
    Direction = auto()
    Visible = auto()
    Name = auto()
    Opts = auto()


REQ_COMP_COL: set[CompoundCol] = set((
    CompoundCol.Name
    , CompoundCol.Energy
))

REQ_REACT_COL: set[ReactionCol] = set((
    ReactionCol.CLeft
    , ReactionCol.CRight
    , ReactionCol.Energy
))


def assure_compound(
    cn: str
    , cs: Sequence[Compound]
) -> Compound:
    """This function serves a wrapper to raise an error in case that the
    compound is not on the list.

    Args:
        cn (:obj:`Compound`): Candidate compound name.
        cs (sequence of :obj:`Compound`): Available candidates.

    Returns:
        Compound: In case that the compound is in the sequence, return the
            :obj:`Compound` with the given name.

    Raises:
        :obj:`ValueError`: If the name is not present in cs.
    """
    try:
        return next(filter(lambda c: c.name == cn, cs))
    except StopIteration:
        raise ValueError(
            f"Compound of name {cn} in reactions not found in compounds"
        )

def apply_maybe(
    fn: Callable[[T,], O]
    , s: T | None
) -> O | None:
    """Given a function fn that takes as an input a value of type T and returns
    a value of type an optional value of type T and O, apply fn only s is not
    None.

    Args:
        fn (function): Function that takes a value of type T as input and
            returns a value of Type O.
        s (any value or None): Value to be used as the input value.


    Returns:
        Either the projected O value or None.
    """
    match s:
        case None: return None
        case _: return fn(s)


def parse_vis(
    s: str
    , default: Visibility = Visibility.TRUE
) -> Visibility:
    """Parses a string representing the visibility of the node. It can be set
    to true, false or grey.

    Args:
        s (str): String to parse.
        default (:obj:`Visibility` or None, optional): Default value to return
            if parsing fails. Defaults to :obj:`Visibility.TRUE`.

    Returns:
        :obj:`Visibility`: Value corresponding to the parsed statement.

    Note:
        The value is lowercased and compared before parsing. t and true and
            parsed as :obj:`Visibility.TRUE`, f and false are parsed as
            :obj:`Visibility.FALSE` and g and grey are parsed as
            :obj:`Visibility.GREY`.

    """
    match s.lower():
        case 't' | 'true': return Visibility.TRUE
        case 'f' | 'false': return Visibility.FALSE
        case 'g' | 'grey' | 'gray': return Visibility.GREY
        case _: return default


def parse_compounds(
    s: str
    , req: set[CompoundCol] = REQ_COMP_COL
) -> tuple[Compound, ...]:
    """Parse compounds in a given string.

    Args:
        s (str): String containing the header and the compounds separated by
            new lines.
        req (set of :opt:`CompoundCol`, optional): Required header values.
            Defaults to :opt:`REQ_COMP_COL`.

    Returns:
        tuple of :obj:`Compound`: A tuple containing the parsed compounds.
    """
    return parse_lines(
        s
        , CompoundCol
        , req
        , parse_compound_line
    )


def parse_compounds_from_file(
    f: str | Path
) -> tuple[Compound, ...]:
    """Wrapper of :obj:`parse_compounds` but using a file as input.

    Args:
        f (str or :obj:`Path`): Name of the file.

    Returns:
        A tuple containing the parsed :obj:`Compound`
    """
    with open(f, 'r') as infile:
        return parse_compounds(infile.read(), REQ_COMP_COL)


def parse_compound_line(
    idx: int
    , l: str
    , h: Sequence[CompoundCol] = tuple(CompoundCol)
) -> Compound:
    """
    Parse a compound line.

    Args:
        idx (int): Index of the compound.
        l (str): Compound line, with values separated by comma.
        h (sequence of :obj:`CompoundCol`): Order of the columns. Defaults to
            the order of :obj:`CompoundCol`.

    Returns:
        :obj:`Compound`: with the given values.

    Note:
        Check :obj:`Compound` for possible values and :obj:`REQ_COMP_COL` for
            required values.
    """
    kw: dict[CompoundCol, str] = dict(
            zip(h, l.split(','))
        )
    vis: str | None = kw.get(CompoundCol.Visible)
    return Compound(
        name=kw[CompoundCol.Name]
        , energy=float(kw[CompoundCol.Energy])
        , idx=idx
        , visible=Visibility.TRUE if vis is None else parse_vis(vis)
        , fflags=apply_maybe(parse_fflags, kw.get(CompoundCol.Fflags))
        , conc=apply_maybe(float, kw.get(CompoundCol.Conc))
        , opts=apply_maybe(parse_opts, kw.get(CompoundCol.Opts)))


def parse_fflags(
    s: str
) -> set[FFlags]:
    """Parse format flags.

    s (str): String to parse. Should contain the format options separated by
        colons.

    Returns:
        set of :obj:`FFlags`: Set containing the parsed format flags.

    Note:
       The format flags are: 'i' for italics, 'b' for bold and 'u' for
           underscore. E.g. i:b.
    """
    return set(filter(
        lambda f: f in s.split(":")
        , list(FFlags)))


def parse_lines(
    s: str
    , h: type[S]
    , r: set[S]
    , fn: Callable[[int, str, list[S]], T]
) -> tuple[T, ...]:
    """Parse a string containing compounds or intermediates in multiple lines.

    Args:
        s (str): String to parse.
        h (:obj:`StrEnum`): Possible column values.
        r (set of str): Required column values.
        fn (:obj:`Callable`[int, str, S] -> T): Function to parse a single line.

    Returns:
        tuple of T: Where T with the parsed values. Where T is the output type
        of :attr:fn.
    """
    rh, *ls = s.splitlines()
    ph: list[S] = list(map(h, rh.split(',')))

    if not r.issubset(h):
        raise ValueError(
            f"Missing column value. Required: {', '.join(r)}"
        )
    return tuple(map(
        lambda xs: fn(xs[0], xs[1], ph)
        , enumerate(ls)
    ))


def parse_network(
    sc: str
    , sr: str
) -> Network:
    """Parse two strings, one containing the compounds of the network and a
    second one containing the reactions of the network. To check how they will
    be parsed, the reader is redicted to the :obj:`parse_compounds` and
    :obj:`parse_reactions` functions.

    Args:
        sc (str): String containing the header and the compounds separated by
            new lines.
        sr (str): String containing the header and the reactions separated by
            new lines.

    Returns:
        :obj:Network: Network with the parsed compounds and reactions.
    """
    cs: tuple[Compound, ...] = parse_compounds(sc, REQ_COMP_COL)
    return Network(
        compounds=cs
        , reactions=parse_reactions(sr, cs, REQ_REACT_COL)
    )


def parse_network_from_file(
    cf: str | Path
    , rf: str | Path
) -> Network:
    """Wrapper of :obj:`parse_network` but using files as input.

    Args:
        cf (str or :obj:`Path`): Name of the file containing the compounds.
        rf (str or :obj:`Path`): Name of the file containing the reactions.

    Returns:
        :obj:Network: Network with the parsed compounds and reactions.
    """
    with open(cf, 'r') as infile:
        sc = infile.read()
    with open(rf, 'r') as infile:
        sr = infile.read()
    return parse_network(sc, sr)


def parse_opts(
    s: str
) -> dict[str, str] | None:
    """Parses the opts column associated with additional opt options.

    Args:
        s (str): String containing the pydot options sopearated by ;.

    Returns:
        dict of [str, str]: keys and values with the opts parsed.

    Note:
        Each option should have a label and a value separated by a '=', and
            different options should be separated with a ':'.
    """
    if s == '': return None
    return dict(map(
        lambda x: x.split('=')
        , s.split(':')
    ))


def parse_reactions(
    s: str
    , cs: Sequence[Compound]
    , req: set[ReactionCol] = REQ_REACT_COL
) -> tuple[Reaction, ...]:
    """Parse reactions in a given string.

    Args:
        s (str): String containing the header and the reactions separated by new
            lines.
        req (set of :obj:`ReactionCol`, optional): Required header values.
            Defaults to :obj:`REQ_COMP_COL`

    Returns:
        tuple of :obj:`Reaction`: Containing the parsed reactions.
    """
    return tuple(chain.from_iterable(parse_lines(
        s
        , ReactionCol
        , req
        , lambda idx, l, h: parse_reaction_line(idx, l, cs, h)
    )))


def parse_reactions_from_file(
    f: str | Path
    , cs: Sequence[Compound]
) -> tuple[Reaction, ...]:
    """Wrapper of :obj:`parse_reactions` but using a file as input.

    Args:
        f (str or Path): Name of the file.

    Returns:
        A tuple containing the parsed :obj:`Reaction`
    """
    with open(f, 'r') as infile:
        return parse_reactions(infile.read(), cs, REQ_REACT_COL)


def parse_reaction_line(
    idx: int
    , l: str
    , cs: Sequence[Compound]
    , h: Sequence[ReactionCol] = tuple(ReactionCol)
) -> tuple[Reaction, ...]:
    """
    Parse a reaction line.

    Args:
        idx (int): Index of the reaction
        l (str): Reaction line.
        cs (sequence of :obj:`Compound`): Sequence of compounds. It will be
            used to get the :obj:`Compound` (by matching name) and reference in
            the reaction instead of using the name.
        h (sequence of :obj:`ReactionCol`): Order of the columns. Defaults to the
            order of :obj:`ReactionCol`.

    Returns:
        :obj:`Reaction`: With the parsed values.

    Note:
        Check :obj:`Reaction` for possible values and :obj:`REQ_REACT_COL` for
            required values.
        Bidirectional reactions will return 2 reactions sharing the same
            idx. idx is intended to track the order of the reaction in the
            reactions file, and thus, I decided to label both reactions with the
            same number.
    """
    def reduce_fn(
        xs: tuple[tuple[list[Compound], list[Compound]], list[tuple[str, str]]]
        , x: tuple[str, str]
    ) -> tuple[tuple[list[Compound], list[Compound]], list[tuple[str, str]]]:
        match x:
            case (_, ""):
                pass
            case (ReactionCol.CLeft, _):
                xs[0][0].append(assure_compound(x[1], cs))
            case (ReactionCol.CRight, _):
                xs[0][1].append(assure_compound(x[1], cs))
            case _:
                xs[1].append(x)
        return xs

    (cl, cr), arg = reduce(
        reduce_fn
        , zip(h, l.split(','))
        , (([], []), [])
    )
    kw: dict[str, str] = dict(arg)
    vis: str | None = kw.get(CompoundCol.Visible)

    ncs: tuple[tuple[tuple[Compound, ...], tuple[Compound, ...]], ...]
    match kw.get(ReactionCol.Direction):
        case Direction.Left:
            ncs = ((tuple(cr), tuple(cl)),)
        case Direction.Biderectional:
            ncs = ((tuple(cr), tuple(cl)), (tuple(cl), tuple(cr)))
        case _:
            ncs = ((tuple(cl), tuple(cr)),)

    return tuple(map(
        lambda xs: Reaction(
            name=str(kw[ReactionCol.Name])
            , compounds=xs
            , energy=float(kw[ReactionCol.Energy])
            , idx=int(idx)
            , visible=Visibility.TRUE if vis is None else parse_vis(vis)
            , opts=apply_maybe(parse_opts, kw.get(CompoundCol.Opts)))
        , ncs
    ))
