"Parser function to read the network in cs form"

from enum import auto, StrEnum
from functools import reduce
from pathlib import Path
from typing import Callable, Sequence, Set, Tuple, TypeVar
from warnings import warn

from .struct import Compound, Direction, Network, Reaction

S = TypeVar('S', bound=StrEnum)
T = TypeVar('T')


class CompoundCol(StrEnum):
    """Posible values for the compound columns."""
    Energy = auto()
    Name = auto()
    Visible = auto()


class ReactionCol(StrEnum):
    """Possible values for the reaction columns."""
    CLeft = auto()
    CRight = auto()
    Energy = auto()
    Direction = auto()
    Visible = auto()
    Name = auto()


REQ_COMP_COL: Set[CompoundCol] = set((
    CompoundCol.Name
    , CompoundCol.Energy
))

REQ_REACT_COL: Set[ReactionCol] = set((
    ReactionCol.CLeft
    , ReactionCol.CRight
))


def parse_compounds(
    s: str
    , req: Set[CompoundCol] = REQ_COMP_COL
) -> Tuple[Compound]:
    """Parse compounds in a given string.

    Args:

    s (str): String containing the header and the compounds separated by
        new lines.
    req (set of `CompoundCol`, optional): Required header values.
        Defaults to `REQ_COMP_COL`

    Returns:
        A tuple containing the parsed `Compound`
    """
    return parse_lines(
        s
        , CompoundCol
        , req
        , parse_compound_line
    )


def parse_compounds_from_file(
    f: str | Path
) -> Tuple[Compound]:
    """Wrapper of `parse_compounds` but using a file as input.

    Args:
        f (str or Path): Name of the file.

    Returns:
        A tuple containing the parsed `Compound`
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
    return Compound(
        name=kw[CompoundCol.Name]
        , idx=idx
        , energy=float(kw[CompoundCol.Energy])
        , visible=bool(kw.get(CompoundCol.Visible) or True)
    )


def parse_lines(
    s: str
    , h: S
    , r: Set[S]
    , fn: Callable[[int, str, S], T]
) -> Tuple[T]:
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
    ph: [S] = list(map(h, rh.split(',')))

    if not r.issubset(h):
        raise ValueError(
            f"Missing column value. Required: {', '.join(r)}"
        )
    return tuple(map(
        lambda xs: fn(
            idx=xs[0]
            , l=xs[1]
            , h=ph
        )
        , enumerate(ls)
    ))


def parse_network(
    sc: str
    , sr: str
) -> Network:
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
    cs = parse_compounds(sc, REQ_COMP_COL)
    return Network(
        compounds=cs
        , reactions=parse_reactions(sr, cs, REQ_REACT_COL)
    )


def parse_network_from_file(
    cf: str | Path
    , rf: str | Path
) -> Network:
    """Wrapper of `parse_network` but using files as input.

    Args:
        cf (str or Path): Name of the file containing the compounds.
        rf (str or Path): Name of the file containing the reactions.

    Returns:
        A tuple containing the parsed `Network`.
    """
    with open(cf, 'r') as infile:
        sc = infile.read()
    with open(rf, 'r') as infile:
        sr = infile.read()
    return parse_network(sc, sr)


def parse_reactions(
    s: str
    , cs: Sequence[Compound]
    , req: Set[ReactionCol] = REQ_REACT_COL
) -> Tuple[Reaction]:
    """Parse reactions in a given string.

    Args:

    s (str): String containing the header and the reactions separated by new
        lines.
    req (set of `ReactionCol`, optional): Required header values.
        Defaults to `REQ_COMP_COL`

    Returns:
        A tuple containing the parsed `Reaction`
    """
    return parse_lines(
        s
        , ReactionCol
        , req
        , lambda idx, l, h: parse_reaction_line(idx, l, cs, h)
    )


def parse_reactions_from_file(
    f: str | Path
) -> Tuple[Reaction]:
    """Wrapper of `parse_reactions` but using a file as input.

    Args:
        f (str or Path): Name of the file.

    Returns:
        A tuple containing the parsed `Reaction`
    """
    with open(f, 'r') as infile:
        return parse_compounds(infile.read(), REQ_COMP_COL)


def parse_reaction_line(
    idx: int
    , l: str
    , cs: Sequence[Compound]
    , h: Sequence[ReactionCol] = tuple(ReactionCol)
) -> Reaction:
    """
    Parse a reaction line.

    Args:
        idx (int): Index of the reaction
        l (str): Reaction line.
        h (sequence of `ReactionCol`): Order of the columns. Defaults to the
            order of `ReactionCol`.

    Returns:
        `Reaction` with the given values.

    Note:
        Check `Reaction` for possible values and `REQ_REACT_COL` for required
        values.
    """

    def gen_react_dict(
        d: dict[ReactionCol, str | Sequence[Compound]]
        , s: [ReactionCol, str]
    ) -> dict[ReactionCol, str | Sequence[Compound]]:
        if not s[1]:
            return d
        if s[0] in (ReactionCol.CLeft, ReactionCol.CRight):
            if s[0] not in d:
                d[s[0]] = []
            try:
                d[s[0]].append(next(filter(
                    lambda c: c.name == s[1]
                    , cs
                )))
            except StopIteration:
                raise ValueError(
                    f"Compound {s[1]} present in reactions not found in the compounds file."
                )
        elif s[0] in d.keys():
            warn(
                f"{s[0]} many instances of s[0] on list. Keeping the first one found"
             )
        else:
            d[s[0]] = s[1]
        return d

    d: dict[ReactionCol, str | Sequence[Compound]] = reduce(
        gen_react_dict
        , zip(h, l.split(','))
        , {}
    )

    return Reaction(
        name = str(d[ReactionCol.Name])
        , idx=int(idx)
        , compounds=(
            d[ReactionCol.CLeft]
            , d[ReactionCol.CRight]
        )
        , direction=Direction(d[ReactionCol.Direction])
        , energy=float(d[ReactionCol.Energy])
        , visible=bool(d.get(ReactionCol.Visible) or True)
    )
