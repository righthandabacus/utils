#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel formatting related functions

The measurement data are from https://bitbucket.org/jky/cpytoxlsf.py
"""

# Font measurement data in pixel width: Calibri 11 normal and bold
CALIBRI = {c: w for s, w in {
    'W@': 377.01 / 28,
    'mM': 348.01 / 28,
    'w%': 319.01 / 28,
    'NOQ&': 290.01 / 28,
    'ADGHUV': 261.01 / 28,
    'bdehnopquBCKPRX': 232.01 / 28,
    '0123456789agkvxyEFSTYZ#$*+<=>?^_|~': 203.01 / 28,
    'cszL"/\\': 174.01 / 28,
    'frtJ!()-[]{}': 145.01 / 28,
    'ijlI,.:;`': 116.01 / 28,
    "' ": 87.01 / 28,
}.items() for c in s}
CALIBRIBOLD = {c: w for s, w in {
    'W': 406.01 / 28,
    'M@': 377.01 / 28,
    'm': 348.01 / 28,
    'w%&': 319.01 / 28,
    'GNOQU': 290.01 / 28,
    'ADHV': 261.01 / 28,
    'bdehnopquBCKPRXY': 232.01 / 28,
    '0123456789agkvxyEFSTZ"#$*+<=>?^_|~': 203.01 / 28,
    'cszL/\\': 174.01 / 28,
    'frtJ!()-[]`{}': 145.01 / 28,
    "ijlI',.:;": 116.01 / 28,
    ' ': 87.01 / 28,
}.items() for c in s}
# Font measurement data in Arial 10, bold size has a factor of 1.1
ARIAL = {c: w for s, w in {
    '@W': 496.356 / 28,
    'Mm': 379.259 / 28,
    '%': 438.044 / 28,
    'CDGOQ': 350.341 / 28,
    '&ABEHKNPRSUVXYw': 321.422 / 28,
    '+<=>F~': 291.556 / 28,
    '#$0123456789?JLTZ_abcdeghnopquy': 262.637 / 28,
    'ksz': 233.244 / 28,
    '*^vx': 203.852 / 28,
    '"()-`r{}': 175.407 / 28,
    ' !,./:;I[\\]f|': 146.015 / 28,
    'it': 117.096 / 28,
    "'jl": 88.178 / 28,
}.items() for c in s}

def pixel2colwidth(pixel_width: float) -> float:
    """Convert text width in pixels into column width. For use in Excel"""
    pixel_width -= 2 if pixel_width > 62 else 1 if pixel_width > 34 else 0
    if pixel_width < 12:
        # first col width unit = 12 pixel
        return pixel_width / 12.0
    else:
        # subsequent col width unit = 7 pixel
        return (pixel_width - 5.0)/7.0

def strwidth(s: str, font: str) -> float:
    """Return string width in pixels. Only limited fonts are allowed.

    Args:
        s: string to measure for width
        font: Any of the following: ["arial10", "arialbold10", "calibri11", "calibribold11"]
    """
    if font == "calibri11":
        fontdict = CALIBRI
    elif font == "calibribold11":
        fontdict = CALIBRIBOLD
    elif font in ["arial10", "arialbold10"]:
        fontdict = ARIAL
    else:
        raise NotImplementedError("Unrecognized font string {}".format(font))
    pixels = 7
    for c in s:
        pixels += fontdict[c]
    if font == "arialbold10":
        pixels *= 1.1
    return pixels

# vim:set ts=4 sw=4 sts=4 tw=100 fdm=indent et:
