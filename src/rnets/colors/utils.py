# -*- coding: utf-8 -*-
"""Utils for Color parsing, writing and interpolation.

Attributes:
    Color (type): Type synonym to define a color.

Note:
    This library only works with 3-D colorspaces. Its extension N-D colorspaces
    should be straightforward, however, it has been decided not to include it
    in benefit of a strict definition of Color.
"""
from collections.abc import Callable, Sequence
from colorsys import rgb_to_hls, hls_to_rgb
from itertools import repeat, starmap
from typing import Literal

type Color = tuple[float, float, float]
type ColorSpace = Literal["rgb", "lab", "hsl"]


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


def cyclic_conditions(
    x: float
    , y: float
) -> tuple[float, float]:
    """Assuming that the range [0, 1] represent a periodic one-dimensional
    space, find the representation of the values that minimizes the distance
    between them.

    Args:
        x (float): First value.
        y (float): Second value.

    Returns:
        A tuple of the form (x, y) containing the new representation of the
        values.
    """
    dist: float = x - y
    if abs(dist) <= 0.5: return (x, y)
    if dist < 0: return (x + 1, y)
    else: return (x, y + 1)


def interp_c_seq(
    x: float
    , cs: Sequence[Color]
    , cyclic: tuple[bool, bool, bool] = (False, False, False)
) -> Color:
    """Given a value float x in the range [0., 1.] and a sequence of colors,
    interpolate a color being represented by x, being 0 the first color in the
    list and 1. the last.

    Args:
        x (float): Floating point number in the range of [0., 1.] representing
            the position in the color sequence.
        cs (Sequence of :obj:`Color`): Sequence of colors to be interpolated.
        cyclic (bool, optional): Index of the components of the color that are
           cyclic. In a cyclic component, the 0 and 1 values are connected, and
           thus the algorithm will consider the shortest path.

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
    comp = map(
        lambda c: (c[0] * (1. - p)) + (c[1] * p)
        , map(
            lambda xs: cyclic_conditions(*xs[:2]) if xs[2] else tuple(xs[:2])
            , zip(cs[idx], cs[idx+1], cyclic)
        )
    )

    a, b, c = map(
        lambda xs: xs[0] - int(xs[0]) if xs[1] else xs[0]
        , zip(comp, cyclic)
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
        return interp_c_seq(x, cs)

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


def interp_fn_cspace(
    cs: Sequence[Color]
    , target: Callable[[float, float, float], Color] = lambda a, b, c: (a,b,c)
    , origin: Callable[[float, float, float], Color] = lambda a, b, c: (a,b,c)
    , cyclic: tuple[bool, bool, bool] = (False, False, False)
) -> Callable[[float], Color]:
    """Given a sequence of :obj:`Color` in an arbitrary colorspace, convert
    them to another space and create an interpolation function. The value
    returned by the interpolation function will be converted again to the
    original colorspace.

    Args:
        cs (Sequence of `Color`): Sequence of colors in the RGB to be converted
            HSL and interpolated.
        target (function of taking three floats as input and returning a
            :obj:`Color`, optional): Function that projects the given color
            components to the colorspace in which the interpolation will be
            performed. Defaults to the identity function.
        origin (function of taking three floats as input and returning a
            :obj:`Color`, optional): Function that returns the interpolated
            color to the original colorspace. Defaults to the identity
            function.
        cyclic (tuple of three bools, optional): During the interpolation,
            treat the dimension marked as True as cyclic. Defaults to (False,
            False, False)

    Returns:
        :obj:Callable[[float], :obj:`Color`]: A function that takes a float in
            the range [0., 1.] as an argument and returns the interpolated
            color from the given Sequence of :obj:`Color` using the specified
            colorspaces.

    Note:
        The :arg:`origin` and :arg:`target` take 3 floats as input for
        to ease the integration with the colorsys library.
    """
    cs_hls: Sequence[Color] = tuple(starmap(target, cs))

    def fn(x: float) -> Color:
        return origin(*interp_c_seq(
            x
            , cs_hls
            , cyclic=cyclic))

    return fn


def interp_fn_rgb_hls(
    cs: Sequence[Color]
) -> Callable[[float], Color]:
    """Given a sequence of :obj:`Color` representing the RGB colorspace,
    convert them to the CIEL*ab space and create an interpolation function. The
    value returned by the interpolation function will be converted again to
    RGB.

    Args:
        cs (Sequence of `Color`): Sequence of colors in the RGB to be converted
            CIEL*ab and interpolated.

    Returns:
        :obj:Callable[[float], :obj:Color]: A function that takes a float in
            the range [0., 1.] as an argument and returns the CIEL*ab interpolated
            color from the given Sequence of RGB :obj:`Color`.
    """
    return interp_fn_cspace(
        cs
        , target=rgb_to_hls
        , origin=hls_to_rgb
        , cyclic=(True, False, False))


def interp_fn_rgb_lab(
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

    Note:
        D65 illuminant. Gamma correction assuming sRGB.

    References:
        CIE Colorimetry 15 (Third ed.). CIE. 2004. ISBN 3-901-906-33-9.
    """
    def t(
        r: float
        , g: float
        , b: float
    ) -> Color:
        l, a, b = xyz_to_lab(*rgb_to_xyz(*map(
            lambda x: apply_gamma(x, None, 1)
            , (r,g,b))))
        return (l, a, b)

    def o(
        l: float
        , a: float
        , b: float
    ) -> Color:
        r, g, b = map(
            lambda x: unapply_gamma(x, None, 1)
            , xyz_to_rgb(*lab_to_xyz(l, a, b)))
        return (r, g, b)

    return interp_fn_cspace(
        cs
        , target=t
        , origin=o
        , cyclic=(False, False, False))


def apply_gamma(
    x: float
    , g: float | None = None
    , A: float = 1.
) -> float:
    """Apply gamma to color component.

    Args:
        x (float): Component to which the Gamma will be applied.
        g (float, optional): Gamma value to apply. If None, assume sRGB
            gamma. Defaults to None.
        A (float, optional): A value for the gamma function. In most cases 1. Defaults to 1.

    Returns:
        Component with the new Gamma value.

    Note:
        The input and the output value are assumed to be a float within the
        [0, 1] interval.
    """
    if g is None:
        return x/12.92 if x < 0.04045 else ((x+0.055)/1.055)**2.4
    else:
        return x**g


def unapply_gamma(
    x: float
    , g: float | None = None
    , A: float = 1.
) -> float:
    """Unapply gammag to color component.

    Args:
        x (float): Component to which the Gamma will be unaapplied.
        g (float, optional): Gamma value to apply. If None, assume sRGB
            gamma. Defaults to None.
        A (float, optional): A value for the gamma function. In most cases 1. Defaults to 1.

    Returns:
        Ungamma component.

    Note:
        The input and the output value are assumed to be a float within the
        [0, 1] interval.
    """
    if g is None:
        return x*12.92 if x <= 0.0031308 else 1.055*(x**((1./2.4))-0.055)
    else:
        return x**(1./g)


def rgb_to_xyz(
    r: float
    , g: float
    , b: float
) -> Color:
    """Projects the given RGB :obj:`Color` value to the L*a*b* colorspace.

    Args:
        r, g, b (float): Floating point number in the interval [0, 1]
            representing the red, green and blue components respectively.

    Returns:
        Projected :obj:`Color`.

    Note:
        Obeserver. = 2, Illuminant = D65

    References:
        Smith, Thomas; Guild, John (1931–32). "The C.I.E. colorimetric
        standards and their use". Transactions of the Optical Society. 33 (3):
        73–134. DOI 10.1088/1475-4878/33/3/301
    """
    return (
        r * 0.4124 + g * 0.3576 + b * 0.1805    # X
        , r * 0.2126 + g * 0.7152 + b * 0.0722  # Y
        , r * 0.0193 + g * 0.1192 + b * 0.9505  # Z
    )


def xyz_to_rgb(
    x: float
    , y: float
    , z: float
) -> Color:
    """Projects the given xyz :obj:`Color` value to the rgb colorspace.

    Args:
        x, y, z (float): Floating point number in the interval [0, 1]
            representing the X, Y and Z components respectively.

    Returns:
        Projected :obj:`Color`.

    Note:
        Obeserver. = 2, Illuminant = D65

    References:
        Smith, Thomas; Guild, John (1931–32). "The C.I.E. colorimetric
        standards and their use". Transactions of the Optical Society. 33 (3):
        73–134. DOI 10.1088/1475-4878/33/3/301
    """
    return (
        x * 3.2406 + y * -1.5372 + z * -0.4968   # R
        , x * -0.9689 + y * 1.8758 + z * 0.0415  # G
        , x * 0.0557 + y * -0.2040 + z * 1.0570  # B
    )


def xyz_to_lab(
    x: float
    , y: float
    , z: float
) -> Color:
    """Projects the given XYZ :obj:`Color` value to the L*a*b* colorspace.

    Args:
        x, y, z (float): Floating point number in the interval [0, 1]
            representing the X, Y, Z components respectively.

    Returns:
        Projected :obj:`Color`.

    References:
        Smith, Thomas; Guild, John (1931–32). "The C.I.E. colorimetric
        standards and their use". Transactions of the Optical Society. 33 (3):
        73–134. DOI 10.1088/1475-4878/33/3/301

        CIE Colorimetry 15 (Third ed.). CIE. 2004. ISBN 3-901-906-33-9.

    Note:
        Adapted from OpenCV.
    """
    x = x / 0.950456
    z = z / 1.088754
    f = lambda t: t**(1./3.) if t > 0.008856 else 7.787*t + 16/116

    return (
        (116.*(y**(1./3.)))-16. if y > 0.008856 else 903.3*y  # L
        , 500.*(f(x) - f(y))                                  # a
        , 200.*(f(y) - f(z))                                  # b
    )


def lab_to_xyz(
    l: float
    , a: float
    , b: float
) -> Color:
    """Projects the given L*a*b :obj:`Color` value to the XYZ colorspace.

    Args:
        l, a, b (float): Floating point number in the interval [0, 1]
            representing the L, a, b components respectively.

    Returns:
        Projected :obj:`Color`.

    References:
        Smith, Thomas; Guild, John (1931–32). "The C.I.E. colorimetric
        standards and their use". Transactions of the Optical Society. 33 (3):
        73–134. DOI 10.1088/1475-4878/33/3/301

        CIE Colorimetry 15 (Third ed.). CIE. 2004. ISBN 3-901-906-33-9.

    Note:
        Adapted from OpenCV.
    """
    y = (l+16.)/116.
    x = (a/500.)+y
    z = y-(b/200.)
    f = lambda t: t**3 if t > 0.008856 else (t-16/116)/7.787

    return(
        f(x) * 0.950456    # X
        , f(y)             # Y
        , f(z) * 1.088754  # Z
    )


def interp_cs(
    cs: Sequence[Color]
    , interp: ColorSpace = "lab"
) -> Callable[[float], Color]:
    """Given a sequence of :obj:`Color` in an arbitrary colorspace, convert
    them to another space and create an interpolation function. The value
    returned by the interpolation function will be converted again to the
    original colorspace.

    Args:
        cs (Sequence of `Color`): Sequence of colors in the RGB to be converted
            HSL and interpolated.
        interp (Literal: rgb, lab or hsl, optional): The colorspace in which
            the interpolation will be perform.


    Returns:
        :obj:Callable[[float], :obj:`Color`]: A function that takes a float in
            the range [0., 1.] as an argument and returns the interpolated
            color from the given Sequence of :obj:`Color` using the specified
            colorspaces.

    Note:
        Wrapper for :obj:`interp_fn_cspace`.
    """

    match interp:
        case "rgb":
            return lambda x: interp_c_seq(x, cs, (False, False, False))
        case "lab": return interp_fn_rgb_lab(cs)
        case "hsl": return interp_fn_rgb_hls(cs)
