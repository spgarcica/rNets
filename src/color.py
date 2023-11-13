from enum import Enum
from itertools import repeat, starmap
from typing import NamedTuple, Tuple, Type, TypeVar



class RGB(NamedTuple):
    """Representation of a color in RGB. All the values are a float in [0, 1]

    Attributes:
        r (float): Red color.
        g (float): Green color.
        b (float): Blue color.
    """
    r: int
    g: int
    b: int


class HSL(NamedTuple):
    """Representation of a color in HSL. All the values are a float in [0, 1]

    Attributes:
        h (float): Hue.
        s (float): Saturation.
        l (float): Lightness.
    """
    h: float
    s: float
    l: float


class Color(NamedTuple):
    """This is a newtype that wraps different colors to ensure type safety.

    Attributes:
        color (`RGB` or `HSL`): Color to use.
    """
    color: RGB | HSL


def ensure_rgb(
    c: Color
) -> bool:
    """Tests wether a `Color` is valid or not.

    Arg:
        c (`Color`): Color to be tested.

    Returns:
        bool representing wether the color is valid or not.
    """

    return all(map(
        lambda x: 0 <= x <= 255
        , c
    ))


def rgb_to_hexstr(
    c: RGB
) -> str:
    """Returns the given color as an hexadecimal string of the form #RRGGBB
    where R, G and B are represented from a number from 0 to 9 and a letter
    from a (10) to f (15).

    Args:
        c (`Color`): `Color` to transform into string.

    Return:
        str of the form #RRGGBB.
    """
    return ('#'
        + ''.join(starmap(
            format
            , zip(c, repeat('02x'))
        )))


def normalize_color(
    c: Color
) -> Tuple[float, float, float]:
    """Normalizes the color to match Python colorsys library.

    Args:
        c (`Color`): Color to normalize.

    Returns:
        Tuple of three floats containing the normalized values
    """
    match c.color:
        case RGB:
            return map(lambda x: x / 255, c.color)
        case HSL:
            return (c.color[0] / 359, c.color[0] / 100, c.color[0] / 100)


def denormalize_color(
    c: Tuple[float, float, float]
    , t: Type[RGB] | Type[HSL]
) ->


def hexstr_to_rgb(
    s: str
) -> RGB | None:
    """Parses a color string of the form #RRGGBB into a `Color`.

    Args:
        s (str): Color string to be parsed.

    Returns:
        `RGB` with the values of the parsed string or None if the conversion
        fails.
    """
    if len(s) != 7 or s[0] != '#':
        return None

    try:
        return Color(*(map(
            lambda x: int("".join(x), 16)
            , zip(s[1::2], s[2::2])
        )))
    except ValueError:
        return None
