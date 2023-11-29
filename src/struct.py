"""Basic structures to encode the reaction"""

from itertools import repeat, starmap
from typing import NamedTuple, Sequence, Tuple


class Compound(NamedTuple):
    """Chemical compound.

    Attributes:
        name (str): Compound name.
        energy (float): Compound energy.
    """
    name: str
    energy: float

    def __str__(self): return self.name

    def __repr__(self):
        return f"[{self.name}]"


class Reaction(NamedTuple):
    """Chemical reaction.

    Attributes:
        name (str): Reaction name.
        compounds (tuple of the form ([`Compound`], [`Compound`])):
           Compounds of the reaction, with Left, Right separation.
        energy (float): Energy of the reaction.
    """
    name: str
    compounds: Tuple[Sequence[Compound], Sequence[Compound]]
    energy: float

    def __str__(self):
        return "->".join(map(
            lambda c: '+'.join(
                starmap(getattr, zip(c, repeat("name")))
            )
            , self.compounds
        ))

    def __repr__(self):
        return f"[{self.name}:{str(self)}]"


class Network(NamedTuple):
    """Representation of a reaction network.

    Attributes:
        compounds (sequence of `Compound`): Compounds of the network.
        reactions (sequence of `Reaction`): Reactions in the network.
    """
    compounds: Sequence[Compound]
    reactions: Sequence[Reaction]
