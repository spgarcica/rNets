# -*- coding: utf-8 -*-
"""Proxy structures to store parsed compounds, reactions and networks.
"""

from collections.abc import Sequence
from enum import auto, Enum, StrEnum
from itertools import repeat, starmap
from typing import NamedTuple


class FFlags(StrEnum):
    """Format flags. They are used to decide the format of the name.

    i -> italics
    b -> bold
    u -> underscore
    """
    I = auto()
    B = auto()
    U = auto()


class Visibility(Enum):
    FALSE = 0
    TRUE = 1
    GREY = 2


class Compound(NamedTuple):
    """Struct for a chemical compound.

    Attributes:
        name (str): Compound name.
        energy (float): Compound energy.
        idx (int): Compound index, in reading order.
        opts (dict of str as keys and str as values or None, optional):
            Additional options for the compound. Will be later used by the
            writer to decide additional options. Defaults to None.
        visible (obj:`Visible`, optional): Wether the compound will be visible,
            grey or not visible. Defaults to :obj:`Visible.TRUE`.
        fflags (set of :obj:`FFlags` or None, optional): Format labels that
            will be used to represent the compound label. Defaults to None.
    """
    name: str
    energy: float
    idx: int
    opts: dict[str, str] | None = None
    visible: Visibility = Visibility.TRUE
    fflags: set[FFlags] | None = None

    def __str__(self): return self.name

    def __repr__(self):
        return f"<{self.name}>"


class Reaction(NamedTuple):
    """Unidirectional chemical reaction.

    Attributes:
        name (str): Reaction name.
        compounds (tuple of the form ([:obj:`Compound`], [:obj:`Compound`])):
           :obj:`Compounds` of the reaction, with left->right direction..
        energy (float): Energy of the reaction.
        idx (int): Reaction index, in reading order.
        opts (dict of str as keys and str as values or None, optional):
            Additional options for the compound. Will be later used by the
            writer to decide additional options. Defaults to None.
        visible (obj:`Visible`, optional): Wether the compound will be visible,
            grey or not visible. Defaults to :obj:`Visible.TRUE`.
    """
    name: str
    compounds: tuple[tuple[Compound, ...], tuple[Compound, ...]]
    energy: float
    idx: int
    opts: dict[str, str] | None = None
    visible: Visibility = Visibility.TRUE

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
        compounds (sequence of :obj:`Compound`): Compounds of the network.
        reactions (sequence of :obj:`Reaction`): Reactions in the network.
    """
    compounds: Sequence[Compound]
    reactions: Sequence[Reaction]
