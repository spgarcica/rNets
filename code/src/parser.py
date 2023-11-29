"Parser function to read the network in cs form"

from enum import auto, StrEnum
from functools import reduce
from itertools import chain
from pathlib import Path
from typing import Callable, Dict, List, NamedTuple, Sequence, Set, Tuple, TypeVar

from .struct import Compound, Reaction

S = TypeVar('S', bound=StrEnum)
T = TypeVar('T')


class CompoundCol(StrEnum):
    """Posible values for the compound columns."""
    Energy = auto()
    Name = auto()
    Visible = auto()
    Opts = auto()
    Fflags = auto()


class Direction(StrEnum):
    """Direction of a reaction. Can be Left, Right or Bidirectional."""
    Left = "<-"
    Right = "->"
    Biderectional = "<->"


class FFlags(StrEnum):
    I = auto()
    B = auto()
    U = auto()


class ReactionCol(StrEnum):
    """Possible values for the reaction columns."""
    CLeft = auto()
    CRight = auto()
    Energy = auto()
    Direction = auto()
    Visible = auto()
    Name = auto()
    Opts = auto()


class PCompound(NamedTuple):
    """Parsed compound.

    Attributes:
        compound (`Compound`): Parsed compound object.
        idx (int): Compound index, in reading order.
        opts (dict of str as keys and str as values or None, optional):
            Additional options for the compound. Will be later used by the
            writer to decide additional options. Defaults to None.
        visible (bool, optional): Wether the compound will be visible or not.
            Defaults to True.
        fflags (set of `FFlags` or None, optional): Format labels that will be
            used to represent the compound label.
    """
    compound: Compound
    idx: int
    opts: Dict[str, str] | None = None
    visible: bool = True
    fflags: Set[FFlags] | None = None


class PReaction(NamedTuple):
    """Parsed reaction.

    Attributes:
        reaction (`Reaction`): Parsed `Reaction`.
        idx (int): Reaction index, in reading order.
        opts (dict of str as keys and str as values or None, optional):
            Additional options for the compound. Will be later used by the
            writer to decide additional options. Defaults to None.
        visible (bool, optional): Wether the compound will be visible or not.
            Defaults to True.

    Note:
        If a bidirectional reaction is specified, more than one reaction can be
        stored reaction.
    """
    reaction: Reaction
    idx: int
    opts: Dict[str, str] | None = None
    visible: bool = True


class PNetwork(NamedTuple):
    """Parsed reaction network containing the parsed compounds and reactions

    Attributes:
        compounds (Sequence of `PCompound`): `PCompounds` of the network.
        reactions (Sequence of `PReaction`): `CReaction` of the network.
    """
    compounds: Sequence[PCompound]
    reactions: Sequence[PReaction]


REQ_COMP_COL: Set[CompoundCol] = set((
    CompoundCol.Name
    , CompoundCol.Energy
))

REQ_REACT_COL: Set[ReactionCol] = set((
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
        cn (`Compound`): Candidate compound name.
        cs (sequence of `Compound`): Available candidates.

    Returns:
        In case that the compound is in the sequence, return the `Compound`
        with the given name.

    Raises:
        ValueError containing some information about the failure.
    """
    try:
        return next(filter(lambda c: c.name == cn, cs))
    except StopIteration:
        raise ValueError(
            f"Compound with name {cn} present in reactions not found in the compounds file."
        )


def parse_bool(
    s: str
) -> bool | None:
    """Parses a string representing a boolean value.

    s (str): String to parse.

    Returns:
        bool value corresponding to the parsed statement. None if the value is
        not parsed.

    Notes:
        The value is lowercased and compared before parsing. t and true and
        parsed as True and f and false are parsed as False.
    """
    match s.lower():
        case 't' | 'true': return True
        case 'f' | 'false': return False
        case _: return None


def parse_compounds(
    s: str
    , req: Set[CompoundCol] = REQ_COMP_COL
) -> Tuple[PCompound, ...]:
    """Parse compounds in a given string.

    Args:

    s (str): String containing the header and the compounds separated by
        new lines.
    req (set of `CompoundCol`, optional): Required header values.
        Defaults to `REQ_COMP_COL`

    Returns:
        A tuple containing the parsed `PCompound`
    """
    return parse_lines(
        s
        , CompoundCol
        , req
        , parse_compound_line
    )


def parse_compounds_from_file(
    f: str | Path
) -> Tuple[PCompound, ...]:
    """Wrapper of `parse_compounds` but using a file as input.

    Args:
        f (str or Path): Name of the file.

    Returns:
        A tuple containing the parsed `PCompound`
    """
    with open(f, 'r') as infile:
        return parse_compounds(infile.read(), REQ_COMP_COL)


def parse_compound_line(
    idx: int
    , l: str
    , h: Sequence[CompoundCol] = tuple(CompoundCol)
) -> PCompound:
    """
    Parse a compound line.

    Args:
        idx (int): Index of the compound.
        l (str): Compound line, with values separated by comma.
        h (sequence of `CompoundCol`): Order of the columns. Defaults to
            the order of `CompoundCol`.

    Returns:
        `Compound` with the given values.

    Note:
        Check `Compound` for possible values and `REQ_COMP_COL` for required
        values.
    """
    kw: dict[CompoundCol, str] = dict(
            zip(h, l.split(','))
        )
    vis: str | None = kw.get(CompoundCol.Visible)
    ffs: str | None = kw.get(CompoundCol.Fflags)
    ops: str | None = kw.get(CompoundCol.Opts)
    return PCompound(
        compound=Compound(
            name=kw[CompoundCol.Name]
            , energy=float(kw[CompoundCol.Energy])
        )
        , idx=idx
        , visible=(parse_bool(vis) if vis else None) or True
        , fflags=parse_fflags(ffs) if ffs else None
        , opts=parse_opts(ops) if ops else None
    )


def parse_fflags(
    s: str
) -> Set[FFlags]:
    """Parse format flags.

    s (str): String to parse. Should contain the format options separated by
        colons.

    Returns:
        set containing the parsed format flags.

    Notes:
       The format flags are: 'i' for italics, 'b' for bold and 'u' for
       underscore. E.g. i:b
    """
    return set(filter(
        lambda f: f in s.split(":")
        , list(FFlags)))


def parse_lines(
    s: str
    , h: type[S]
    , r: Set[S]
    , fn: Callable[[int, str, List[S]], T]
) -> Tuple[T, ...]:
    """Parse a string containing compounds or intermediates in multiple lines.

    Args:
        s (str): String to parse.
        h (StrEnum): Possible column values.
        r (set of strings): Required column values.
        fn (function [int, str, S] -> T): Function to parse a single line.

    Returns:
        A tuple containing the parsed values.
    """
    rh, *ls = s.splitlines()
    ph: List[S] = list(map(h, rh.split(',')))

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
) -> PNetwork:
    """Parse two strings, one containing the compounds of the network and a
    second one containing the reactions of the network. To check how they will
    be parsed, the reader is redicted to the `parse_compounds` and 
    `parse_reactions` functions.

    Args:
        sc (str): String containing the header and the compounds separated by
            new lines.
        sr (str): String containing the header and the reactions separated by
            new lines.

    Returns:
        Network with the parsed compounds and reactions.
    """
    cs: Tuple[PCompound, ...] = parse_compounds(sc, REQ_COMP_COL)
    return PNetwork(
        compounds=cs
        , reactions=parse_reactions(
            sr
            , tuple(map(lambda c: c.compound, cs))
            , REQ_REACT_COL
        )
    )


def parse_network_from_file(
    cf: str | Path
    , rf: str | Path
) -> PNetwork:
    """Wrapper of `parse_network` but using files as input.

    Args:
        cf (str or Path): Name of the file containing the compounds.
        rf (str or Path): Name of the file containing the reactions.

    Returns:
        A tuple containing the parsed `PNetwork`.
    """
    with open(cf, 'r') as infile:
        sc = infile.read()
    with open(rf, 'r') as infile:
        sr = infile.read()
    return parse_network(sc, sr)


def parse_opts(
    s: str
) -> Dict[str, str]:
    """Parses the opts column associated with additional opt options.

    Args:
        s (str): String containing the pydot options sopearated by ;.

    Returns:
        dict with str as keys and values with the opts parsed.

    Notes:
        Note that each options should have a label and a value separated by a
        '=', and different options should be separated with a ':'.
    """
    return dict(map(
        lambda x: x.split('=')
        , s.split(':')
    ))


def parse_reactions(
    s: str
    , cs: Sequence[Compound]
    , req: Set[ReactionCol] = REQ_REACT_COL
) -> Tuple[PReaction, ...]:
    """Parse reactions in a given string.

    Args:

    s (str): String containing the header and the reactions separated by new
        lines.
    req (set of `ReactionCol`, optional): Required header values.
        Defaults to `REQ_COMP_COL`

    Returns:
        A tuple containing the parsed `Reaction`
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
) -> Tuple[PReaction, ...]:
    """Wrapper of `parse_reactions` but using a file as input.

    Args:
        f (str or Path): Name of the file.

    Returns:
        A tuple containing the parsed `PReaction`
    """
    with open(f, 'r') as infile:
        return parse_reactions(infile.read(), cs, REQ_REACT_COL)


def parse_reaction_line(
    idx: int
    , l: str
    , cs: Sequence[Compound]
    , h: Sequence[ReactionCol] = tuple(ReactionCol)
) -> Tuple[PReaction, ...]:
    """
    Parse a reaction line.

    Args:
        idx (int): Index of the reaction
        l (str): Reaction line.
        cs (sequence of `Compound`): Sequence of compounds. It will be used to
            get the `Compounds` (by matching name) and reference in the reaction
            instead of using the name.
        h (sequence of `ReactionCol`): Order of the columns. Defaults to the
            order of `ReactionCol`.

    Returns:
        `Reaction` with the given values.

    Note:
        Check `Reaction` for possible values and `REQ_REACT_COL` for required
        values.

        Bidirectional reactions will return 2 reactions sharing the same
        idx. idx is intended to track the order of the reaction in the
        reactions file, and thus, I decided to label both reactions with the
        same number.
    """
    def reduce_fn(
        xs: Tuple[Tuple[List[Compound], List[Compound]], List[Tuple[str, str]]]
        , x: Tuple[str, str]
    ) -> Tuple[Tuple[List[Compound], List[Compound]], List[Tuple[str, str]]]:
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
    ops: str | None = kw.get(CompoundCol.Opts)

    ncs: List[Tuple[List[Compound], List[Compound]]]
    match kw.get(ReactionCol.Direction):
        case Direction.Left:
            ncs = [(cr, cl)]
        case Direction.Right :
            ncs = [(cl, cr)]
        case Direction.Biderectional:
            ncs = [(cr, cl), (cl, cr)]
        case _:
            ncs = [(cl, cr)]

    return tuple(map(
        lambda xs: PReaction(
            reaction=Reaction(
                name=str(kw[ReactionCol.Name])
                , compounds=xs
                , energy=float(kw[ReactionCol.Energy])
            )
            , idx=int(idx)
            , visible=(parse_bool(vis) if vis else None) or True
            , opts=parse_opts(ops) if ops else None
        )
        , ncs
    ))
