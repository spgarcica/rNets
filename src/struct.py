"""Basic structures to encode the reaction"""

from enum import auto, StrEnum
from itertools import repeat, starmap
from typing import NamedTuple, Sequence, Tuple


class Direction(StrEnum):
    """Direction of the reaction. Can be Left, Right or Bidirectional."""
    Left = "<-"
    Right = "->"
    Biderectional = "<->"


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


class Compound(NamedTuple):
    """Chemical compound.

    Attributes:
        name (str): Compound name.
        idx (int): Compound index.
        energy (float): Compound energy.
        visible (bool, optional): Wether of not the reaction will be visible.
            Defaults to True.
    """
    name: str
    idx: int
    energy: float
    visible: bool = True

    def __str__(self): return self.name

    def __repr__(self):
        v = (",H", "")[self.visible]
        return f"[{self.idx}{v}]{self.name}"


class Reaction(NamedTuple):
    """Chemical reaction.

    Attributes:
        name (str): Reaction name.
        idx (int): Reaction index.
        compounds (tuple of the form ([`Compound`], [`Compound`])):
           Compounds of the reaction, with Left, Right separation.
        direction (Direction): Reaction direction.
        energy (float): Energy of the associated transition state.
        visible (bool): Wether of not the reaction will be visible.
            Defaults to True.
    """
    name: str
    idx: int
    compounds: Tuple[Sequence[Compound], Sequence[Compound]]
    direction: Direction
    energy: float
    visible: bool = True

    def __str__(self):
        return self.direction.join(map(
            lambda c: '+'.join(
                starmap(getattr, zip(c, repeat("name")))
            )
            , self.compounds
        ))

    def __repr__(self):
        v = (",H", "")[self.visible]
        return f"[{self.idx},{self.name}{v}]{str(self)}"


class Network(NamedTuple):
    """Representation of a reaction network.

    Attributes:
        compounds (sequence of `Compound`): Compounds of the network.
        reactions (sequence of `Reaction`): Reactions in the network.
    """
    compounds: Sequence[Compound]
    reactions: Sequence[Reaction]
