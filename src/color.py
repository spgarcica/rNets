"Color parsing, writing and interpolation."

from colorsys import rgb_to_hls, hls_to_rgb
from itertools import repeat, starmap
from typing import Callable, Sequence, Tuple

Color = Tuple[float, float, float]


def ensure_color(
    c: Color
) -> bool:
    """Tests wether a `Color` is valid or not.

    Arg:
        c (`Color`): Color to be tested.

    Returns:
        bool representing wether the color is valid or not.

    Notes:
        Note that `Color` follows the colorsys representation, meaning that it
        consists of 3 float values ranging from [0, 1].
    """
    return all(map(
        lambda x: 0. <= x <= 1.
        , c
    ))


def rgb_to_hexstr(
    c: Color
) -> str:
    """Returns the given color as an hexadecimal string of the form #RRGGBB
    where R, G and B are represented from a number from 0 to 9 and a letter
    from a (10) to f (15).

    Args:
        c (`Color`): `Color` to transform into string.

    Return:
        str of the form #RRGGBB.

    Notes:
        Note that `Color` follows the colorsys representation, meaning that it
        consists of 3 float values ranging from [0, 1].
    """
    return ('#'
        + ''.join(starmap(
            format
            , zip(
                map(lambda x: round(x * 255), c)
                , repeat('02x'))
        )))


def hexstr_to_rgb(
    s: str
) -> Color | None:
    """Parses a color string of the form #RRGGBB into a `Color`.

    Args:
        s (str): Color string to be parsed.

    Returns:
        `RGB` with the values of the parsed string or None if the conversion
        fails.

    Notes:
        Note that `Color` follows the colorsys representation, meaning that it
        consists of 3 float values ranging from [0, 1].
    """
    if len(s) != 7 or s[0] != '#':
        return None

    try:
        # Force only three values in the tuple
        a, b, c =map(
            lambda x: float(int("".join(x), 16)) / 255.
            , zip(s[1::2], s[2::2])
        )
        return (a, b, c)
    except ValueError:
        return None


def interp(
    x: float
    , cs: Sequence[Color]
) -> Color:
    """Given a value float x in the range [0., 1.] and a sequence of colors,
    interpolate a color being represented by x, being 0 the first color in the
    list and 1. the last.

    Args:
        x (float): Floating point number in the range of [0., 1.] representing
            the position in the color sequence.
        cs (Sequence of `Color`): Sequence of colors to be interpolated.

    Returns:
        Interpolated `Color` using the colorsys implementation (3 float values
        in [0. ,1.])

    Notes:
        Note that this function will perform the interpolation withing the
        color space provided. i. e. if RGB is used, the interpolation will be
        done within the RGB colorspace. If x overflows on the roof, the last
        color of the sequence is returned while if x overflows on the floor,
        the first color of the sequence is returned.
    """
    # Ensure x in [0, 1]
    if x >= 1.:
        return cs[-1]
    if x <= 0.:
        return cs[0]

    val: float = (x * (len(cs) - 1))
    idx: int = int(val)
    p: float = val - idx

    # Force 3 values in the tuple
    a, b, c =map(
        lambda c: (c[0] * (1. - p)) + (c[1] * p)
        , zip(cs[idx], cs[idx + 1])
    )

    return (a, b, c)


def interp_fn(
    cs: Sequence
) -> Callable[[float], Color]:
    """Given a sequence of `Colors`, returns an interpolated function based on
    it.

    Args:
        cs (Sequence of `Color`): Sequence of colors to be interpolated.

    Returns:
        A function that takes a float in the range [0., 1.] as an argument and
        returns the interpolated color from the given Sequence of `Color`.

    Notes:
        This function acts as a wrapper of `interp`.
    """
    def fn(x: float) -> Color:
        return interp(x, cs)

    return fn


def interp_fn_rgb_hls(
    cs: Sequence[Color]
) -> Callable[[float], Color]:
    """Given a sequence of `Color` representing the RGB colorspace, convert
    them to the HSL space and create and interpolation function. The value
    returned by the interpolation function will be converted again to rgb.

    Args:
        cs (Sequence of `Color`): Sequence of colors in the RGB to be converted
            HSL and interpolated.

    Returns:
        A function that takes a float in the range [0., 1.] as an argument and
        returns the HSL interpolated color from the given Sequence of RGB
        `Color`.
    """
    cs_hls: Sequence[Color] = tuple(starmap(rgb_to_hls, cs))

    def fn(x: float) -> Color:
        return hls_to_rgb(*interp(x, cs_hls))

    return fn
