# -*- coding: utf-8 -*-
"""Utils for Color parsing, writing and interpolation.

Attributes:
    Color (type): Type synonym to define a color.
"""
from collections.abc import Callable, Sequence
from colorsys import rgb_to_hls, hls_to_rgb
from itertools import repeat, starmap


Color = tuple[float, float, float]


def ensure_color(
    c: Color
) -> bool:
    """Tests wether a :obj:`Color` is valid or not.

    Arg:
        c (:obj:`Color`): Color to be tested.

    Returns:
        bool: wether the color is valid or not.

    Note:
        :obj:`Color` follows the colorsys representation, meaning that it
            consists of 3 float values ranging from [0, 1].
    """
    return all(map(
        lambda x: 0. <= x <= 1.
        , c
    ))


def rgb_to_hexstr(
    c: Color
    , inc_hash: bool = True
) -> str:
    """Returns the given color as an hexadecimal string of the form #RRGGBB
    where R, G and B are represented from a number from 0 to 9 and a letter
    from a (10) to f (15).

    Args:
        c (:obj:`Color`): :obj:`Color` to transform into string.
        inc_hash (bool, optional): If True, include the hash character at the
            beggining of the color string. Defaults to True.

    Returns:
        str: Color string with the RRGGBB form.

    Note:
        Note that :obj:`Color` follows the :obj:`colorsys representation,
            meaning that it consists of 3 float values ranging from [0, 1].
    """
    return ('#' * inc_hash
        + ''.join(starmap(
            format
            , zip(
                map(lambda x: round(x * 255), c)
                , repeat('02x'))
        )))


def hexstr_to_rgb(
    s: str
) -> Color | None:
    """Parses a color string of the form #RRGGBB into a :obj:`Color`.

    Args:
        s (str): Color string to be parsed.

    Returns:
        :obj:`Color`: With the values of the parsed string
        None: If the conversion fails.

    Note:
        Note that :obj:`Color` follows the :obj:`colorsys representation,
            meaning that it consists of 3 float values ranging from [0, 1].
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
        cs (Sequence of :obj:`Color`): Sequence of colors to be interpolated.

    Returns:
        :obj:`Color`: Interpolation using the :obj:colorsys implementation (3
            float values in [0. ,1.])

    Note:
        Note that this function will perform the interpolation withing the
            color space provided. i. e. if RGB is used, the interpolation will
            be done within the RGB colorspace. If x overflows on the roof, the
            last color of the sequence is returned while if x overflows on the
            floor, the first color of the sequence is returned.
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


def rgb_achromatize(
    c: Color
) -> Color:
    """Achromatize the given RGB color.

    Args:
        c (:obj:`Color`): Color that will be achromatized.

    Returns:
        :obj:`Color` Achromatized color.

    Note:
        Formula taken from the pillow library:
        https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.convert

    """
    Y: float = (
        c[0] * 0.299
        + c[1] * 0.587
        + c[2] * 0.114
    )
    return (Y, Y, Y)


def interp_fn(
    cs: Sequence
) -> Callable[[float], Color]:
    """Given a sequence of :obj:`Color`, returns an interpolated function based
    on it.

    Args:
        cs (Sequence of :obj:`Color`): Sequence of colors to be interpolated.

    Returns:
        :obj:Callable[[float], :obj:`Color`]: A function that takes a float in
            the range [0., 1.] as an argument and returns the interpolated
            color from the given Sequence of :obj:`Color`.

    Note:
        This function acts as a wrapper of :obj:`interp`.
    """
    def fn(x: float) -> Color:
        return interp(x, cs)

    return fn


def calc_relative_luminance(
    c: Color
) -> float:
    """Calculate the relative luminance of a :obj:`Color` in the RGB space.

    Args:
        c (:obj:`Color`): Color in the RGB colorspace to compute its luminance.

    Returns:
        float:  Computed luminance.

    References:
        https://www.w3.org/WAI/GL/wiki/Relative_luminance
    """
    return (
        0.2126 * c[0]
        + 0.7152 * c[1]
        + 0.0722 * c[2]
    )


def color_sel_lum(
    c1: Color
    , c2: Color
    , dc: Color
    , threshold: float = 0.5
) -> Color:
    """Given a pair of colors, select a color from it based on the relative
    luminance of a third one.

    Args:
        c1 (:obj:`Color`): Color to select if the luminance is below the
            threshold.
        c2 (:obj:`Color`): Color to select if the luminance is above the
            threshold.
        dc (:obj:`Color`): Color to use to compute the relative luminance.
        threshold (float, optional): Threshold to make the decision. Ideally, a
            value between 0. and 1. Defaults to 0.5.

    Returns:
       :obj:`Color`: c1 or c2.
    """
    return (c1, c2)[calc_relative_luminance(dc) < threshold]


def interp_fn_rgb_hls(
    cs: Sequence[Color]
) -> Callable[[float], Color]:
    """Given a sequence of :obj:`Color` representing the RGB colorspace,
    convert them to the HSL space and create an interpolation function. The
    value returned by the interpolation function will be converted again to
    rgb.

    Args:
        cs (Sequence of `Color`): Sequence of colors in the RGB to be converted
            HSL and interpolated.

    Returns:
        :obj:Callable[[float], :obj:Color]: A function that takes a float in
            the range [0., 1.] as an argument and returns the HSL interpolated
            color from the given Sequence of RGB :obj:`Color`.
    """
    cs_hls: Sequence[Color] = tuple(starmap(rgb_to_hls, cs))

    def fn(x: float) -> Color:
        return hls_to_rgb(*interp(x, cs_hls))

    return fn
