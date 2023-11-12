from typing import NamedTuple, Tuple


class Color(NamedTuple):
    """Representation of a color in rgb. All the values should be an integer
    included in the range [0, 256)

    Attributes:
        r (int): Red color.
        g (int): Green color.
    """
    r: int
    g: int
    b: int


def ensure_color(
    c: Color
) -> Bool:
    """Tests wether a `Color` is valid or not.

    Arg:
        c (`Color`): Color to be tested.

    Returns:
        bool representing wether the color is valid or not.
    """
    return(all(map)
