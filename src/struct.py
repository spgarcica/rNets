"""Basic structures to encode the reaction"""

from enum import auto, StrEnum
from itertools import repeat, starmap
from typing import Dict, NamedTuple, Set, Sequence, Tuple


class FFlags(StrEnum):
    """Format flags. They are used to decide the format of the name.

    i -> italics
    b -> bold
    u -> underscore
    """
    I = auto()
    B = auto()
    U = auto()


class Compound(NamedTuple):
    """Struct for a chemical compound.

    Attributes:
        name (str): Compound name.
        energy (float): Compound energy.
        idx (int): Compound index, in reading order.
        opts (dict of str as keys and str as values or None, optional):
            Additional options for the compound. Will be later used by the
            writer to decide additional options. Defaults to None.
        visible (bool, optional): Wether the compound will be visible or not.
            Defaults to True.
        fflags (set of `FFlags` or None, optional): Format labels that will be
            used to represent the compound label.
    """
    name: str
    energy: float
    idx: int
    opts: Dict[str, str] | None = None
    visible: bool = True
    fflags: Set[FFlags] | None = None

    def __str__(self): return self.name

    def __repr__(self):
        return f"<{self.name}>"


class Reaction(NamedTuple):
    """Chemical reaction.

    Attributes:
        name (str): Reaction name.
        compounds (tuple of the form ([`Compound`], [`Compound`])):
           Compounds of the reaction, with Left, Right separation.
        energy (float): Energy of the reaction.
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
    name: str
    compounds: Tuple[Tuple[Compound, ...], Tuple[Compound, ...]]
    energy: float
    idx: int
    opts: Dict[str, str] | None = None
    visible: bool = True

    def __str__(self):
        return "->".join(map(
            lambda c: '+'.join(
                starmap(getattr, zip(c, repeat("name")))
            )
            , self.compounds
        ))

    def __repr__(self):
        return f"<{self.name}:{str(self)}>"


class Network(NamedTuple):
    """Representation of a reaction network.

    Attributes:
        compounds (sequence of `Compound`): Compounds of the network.
        reactions (sequence of `Reaction`): Reactions in the network.
    """
    compounds: Sequence[Compound]
    reactions: Sequence[Reaction]
