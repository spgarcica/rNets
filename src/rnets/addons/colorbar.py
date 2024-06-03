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

from functools import partial
from itertools import pairwise, starmap
from typing import NamedTuple, Sequence, Callable

from rnets.dot import Edge, IDENT, ident_if, Node
from rnets.colors.utils import Color, rgb_to_hexstr

type Attribute = dict[str, str]

OPEN_MARK = '<'
CLOSE_MARK = '>'
ATTR_SEPARATOR = ' '
ATTR_ASSIGN = '='


class ColorbarCfg(NamedTuple):
    """Structure representing the colorbar configuration.

    Attributes:

        n_interp (int, optional): Number of color segments. Defaults to 100.
        width (int, optional): Width of each color segment, in HTML table
            units. Defaults to 1.
        height (int, optional): Height of the colorbar, in HTML table
            units. Defaults to 20.
        cellspacing (int, optional): Space between the different color
            segments in HTML table units. Keep a negative value to ensure
            uniform perception. Defaults to -1.
        node_name (str, optional): Name of the generated node. Defaults to
            Colorbar.
        fillcolor (obj:`Color`, optional): Color of the node. Defaults to
            white.
        anchor_node (str or None): Node to anchor the colorbar. Defaults to None
    """
    n_interp: int | None = 100
    width: int = 1
    height: int = 20
    border: bool = False
    cellspacing: int = -1
    node_name: str = "Colorbar"
    fillcolor: Color = (1., 1., 1.)
    anchor: str | None = None


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
    contains: 'Sequence[Item] | str | None'

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


def match_contains(
    contains: Sequence[Item] | str | None
) -> str:
    match contains:
        case str(): return contains
        case None: return ''
        case _: return "\n{}\n".format(
                ident_if(
                    '\n'.join(map(item_to_str, contains))
                    , IDENT
                    , True))


def item_to_str(
    item: Item | None
    , separator: str = '\n'
) -> str:
    """Convert an item into a string.

    Args:
        item (obj:`Item` or None): Item to be converted.
        separator (str): Separator between the different contains.

    Returns:
        str with the HTML form of the item.
    """
    match item:
        case None: return ''
        case Item(): return (
            OPEN_MARK + item.name
            + (f' {v}' if (v := attr_to_str(item.attributes)) else '')
            + CLOSE_MARK
            + match_contains(item.contains)
            + OPEN_MARK + '/' + item.name + CLOSE_MARK)
        case _: return ''


def build_node(
    item: Item
    , name: str
    , fillcolor: Color
) -> Node:
    """Given an obj:`Item`, create a dot node using the str form of the item as
    a the node label.

    Args:
        item (obj:`item`): Item that will be converted into a Node.
        name (str, optional): Name of the generated node.
        fillcolor (obj:`Color`): Color of the node.

    Returns:

        obj:`Node` built node using the str form of the item as the label.
    """
    return Node(
        name
        , options={
            "fillcolor": '"{}"'.format(rgb_to_hexstr(fillcolor, True))
            , "label": OPEN_MARK + item_to_str(item) + CLOSE_MARK
        })


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
    return Item("TR", {}, (Item("TD", {"COLSPAN": "100%"}, (
        Item(
            "TABLE"
            , {"BORDER": "0", "CELLBORDER": "0", "CELLSPACING": "0", "WIDTH":"100%"}
            , (Item("TR", {}, (
                Item("TD", {"ALIGN": "LEFT", "WIDTH": "33%"}
                     , f"{c_min:.2f}")
                , Item("TD", {"ALIGN": "CENTER", "WIDTH": "34%"}
                       , f"{(c_min + c_max)/2:.2f}")
                , Item("TD", {"ALIGN": "RIGHT", "WIDTH": "33%"}
                       , f"{c_max:.2f}"))),)),)),))


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
        , None)


def build_head(
    title: str
    , n_interp: int
) -> Item:
    return Item("TR", {}, (
        Item("TD"
             , {"COLSPAN": str(n_interp)}
             , title),))


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
    return (Item(
        "TR", {}
        , map(
            partial(build_color_segment, width=width, height=height)
            , pairwise(map(
                lambda x: color_fn(x / n_interp)
                , range(n_interp + 1)))),))


def build_colorbar(
    color_fn: Callable[[float], Color]
    , c_ran: tuple[float, float] | None
    , cfg: ColorbarCfg
    , title: str | None="Energy"
) -> Node:
    """Given a obj:`ColorbarCfg` build the associated graphviz obj:`Node`.

    Args:
        color_fn (function taking a [0,1] float as input and returning a
            obj:`Color`): Color interpolation function.
        c_ran (tuple of two floats, optional): Minimum and maximum energy
             values. Defaults to None
        cfg (obj:`ColorbarCfg`): Configuration used to build the colorbar.
        title (str, optional): Title of the colorbar. Defaults to None.


    Returns:
        obj:`Node` built from the given configuration.
    """
    return build_node(
        Item(
            "TABLE"
            , {"BORDER": str(int(cfg.border))
               , "CELLBORDER": "0"
               , "CELLSPACING": str(int(cfg.cellspacing))}
            , (build_head(title, cfg.n_interp)
               , build_body(color_fn, cfg.n_interp, cfg.width, cfg.height)
               , None if c_ran is None else build_tail(*c_ran)))
        , name=cfg.node_name
        , fillcolor=cfg.fillcolor)


def build_anchor(
    origin: Node
    , target: Node
) -> Edge:
    return Edge(
        origin=origin
        , target=target
        , direction="->"
        , options={"style": "invis"})
