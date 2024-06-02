# -*- coding: utf-8 -*-
"""This module aims to create an horizontal node colorbar that can be easily
attached to a dot graph. This node is created as a HTML table of 3 rows and
multiple columns. Each column contains the interpolation two color segment for
the given colorscheme.

Attributes:
    Attribute (type): Type synonym to define the attributes of an HTML table.
    OPEN_MARK (str): Open HTML character.
    CLOSE_MARK (str): Close HTML character.
    ATTR_SEPARATOR (str): HTML attribute separator character.
    ATTR_ASSIGN (str): HTML assignement character.
"""

from itertools import starmap
from typing import NamedTuple, Sequence, Callable

from rnets.dot import IDENT, ident_if, Node
from rnets.colors.utils import Color, rgb_to_hexstr

type Attribute = dict[str, str]

OPEN_MARK = '<'
CLOSE_MARK = '>'
ATTR_SEPARATOR = ' '
ATTR_ASSIGN = '='


class ColorbarCfg(NamedTuple):
    """Structure representing the colorbar configuration.

    Attributes:
        color_fn (function taking a [0,1] float as input and returning a
            obj:`Color`): Color interpolation function.
        title (str, optional): Title of the colorbar. Defaults to None.
        c_ran (tuple of two floats, optional): Minimum and maximum energy
             values. Defaults to None
        n_interp (int, optional): Number of color segments. Defaults to 100.
        width (int, optional): Width of each color segment, in HTML table
            units. Defaults to 1.
        height (int, optional): Height of the colorbar, in HTML table
            units. Defaults to 20.
        cellspacing (int, optional): Space between the different color
            segments in HTML table units. Keep a negative value to ensure
            uniform perception. Defaults to -1.
        node_name: (str, optional): Name of the generated node. Defaults to
            Colorbar.
    """
    color_fn: Callable[[float], Color]
    title: str | None = None
    c_ran: tuple[float, float] | None = None
    n_interp: int | None = 100
    width: int = 1
    height: int = 20
    border: bool = False
    cellspacing: int = -1
    node_name: str = "Colorbar"


class Item(NamedTuple):
    """HTML element.

    Attributes:
        name (str): Name of the HTML element.
        attributes (Attribute or None): Attributes of the HTML element.
        contains (Sequence of item or str or None): Items or values inside the
            HTML element.
    """
    name: str
    attributes: Attribute | None
    contains: 'Sequence[Item | str] | None'

    def __str__(self):
        return item_to_str(self)


def attr_to_str(
    attr: Attribute
    , separator: str=ATTR_SEPARATOR
    , assign: str=ATTR_ASSIGN
) -> str:
    """Converts the given attribute into a str.

    Args:
        attr (`attribute`): Attribute to be converted.
        separator (str, optional): Separator between the different attribute
           options. Defaults to `ATTR_SEPARATOR`.
        assign (str, optional): Assignment operator. Defaults to `ATTR_ASSIGN`.

    Returns:
        str of the attribute with the given format: KEY:\"VALUE\"
    """
    return separator.join(starmap(
        lambda k, v: f'{k}{assign}"{v}"'
        , attr.items()))


def item_to_str(
    item: Item | str
    , separator: str = '\n'
) -> str:
    """Convert an item into a string.

    Args:
        item (obj:`Item`): Item to be converted.
        separator (str): Separator between the different contains.

    Returns:
        str with the HTML form of the item.
    """
    match item:
        case str():
            return item
        case Item(): return (
            ((OPEN_MARK + v) if (v := item.name) else '')
            + (f' {v}' if (v := attr_to_str(item.attributes)) else '')
            + CLOSE_MARK
            + (f'\n{v}\n' if (v := ident_if(
                separator.join(map(item_to_str, item.contains))
                , IDENT))
               else '')
            + OPEN_MARK + '/' + item.name + CLOSE_MARK)


def build_node(
    item: Item
    , name: str
) -> Node:
    """Given an obj:`Item`, create a dot node using the str form of the item as
    a the node label.

    Args:
        item (obj:`item`): Item that will be converted into a Node.
        name (str, optional): Name of the generated node.

    Returns:
        obj:`Node` built node using the str form of the item as the label.
    """
    return Node(
        name
        , options={"label": OPEN_MARK + item_to_str(item) + CLOSE_MARK})


def build_tail(
    c_min: float
    , c_max: float
) -> Item:
    """Build the tail of the colorbar marking the starting, mid and final
    energy values. Always places 2 decimal values.

    Args:
        c_min (float): Minimum energy value.
        c_max (float): Maximum energy value.

    Returns:
        HTML row with the start, mid and end values of the energy.
    """
    return Item(
        "TABLE"
        , {"BORDER": "0", "CELLBORDER": "0", "CELLSPACING": "0", "WIDTH":"100%"}
        , (Item("TR", {}, (
            Item("TD", {"ALIGN": "LEFT", "WIDTH": "33%"}
                 , (f"{c_min:.2f}",))
            , Item("TD", {"ALIGN": "CENTER", "WIDTH": "34%"}
                 , (f"{(c_min + c_max)/2:.2f}",))
            , Item("TD", {"ALIGN": "CENTER", "WIDTH": "34%"}
                , (f"{c_max:.2f}",)))),))


def build_color_segment(
    cs: (Color, Color)
    , width: int
    , height: int
) -> Item:
    """Given a pair of obj:`Color`, build a HTML cell containing an horizontal
    gradient.

    Args:
        cs (Color, Color): Color pair that will be interpolated in the segment.
        width (int): Width of the segment, in HTML table units.
        height (int): Height of the segment, in HTML table units.

    Returns:
        obj:`Item` of the generated segment.
    """
    return Item("TD"
        , {"BGCOLOR": f"{rgb_to_hexstr(cs[0])}:{rgb_to_hexstr(cs[1])}"
           , "WIDTH": str(width)
           , "HEIGHT": str(height)}
        , ())


def build_body(
    color_fn: Callable[[float], Color]
    , n_interp: int
    , width: int
    , height: int
) -> Item:
    """Build the entire colorbar row.

    Args:
        color_fn (Callable[[float], Color]): Color interpolation function.
        n_interp (int): Number of columns.
        width (int): Width of the segment, in HTML table units.
        height (int): Height of the segment, in HTML table units.

    Returns:
       obj:`Item` of the generated row.
    """
    return (
        Item("TR", {}, (
            Item("TD"
                , {"COLSPAN": str(n_interp)}
                , ("Energy",)),))
        , Item("TR", {}
            , map(
                build_color_segment
                , pairwise(map(
                    lambda x: color_fn(x / n_interp)
                    , range(n_interp + 1)))),),)


def build_colorbar(
    cfg: ColorbarCfg
) -> Node:
    """Given a obj:`ColorbarCfg` build the associated graphviz obj:`Node`.

    Args:
        cfg (obj:`ColorbarCfg`): Configuration used to build the colorbar.

    Returns:
        obj:`Node` built from the given configuration.
    """
    return build_node(
        Item(
            "TABLE"
            , {"BORDER": str(int(cfg.border))
               , "CELLBORDER": "0"
               , "CELLSPACING": str(int(cfg.cellspacing))}
            , ("Item", {"COLSPAN": str(cfg.n_interp)}, (cfg.title,)
               , build_body(cfg.color_fn, cfg.n_interp, cfg.width, cfg.height)
               , '' if cfg.c_ran is None else build_tail(*cfg.c_ran)))
        , name=cfg.node_name)
