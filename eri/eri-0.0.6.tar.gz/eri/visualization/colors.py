#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: colors.py
Author: zlamberty
Created: 2016-05-18

Description:
    module to contain possibly shared color functions. Fundamental
    representation types are dictionaries with the usual keys
    (rgb(a), cmyk, hsv(a)) and hex codes, but I also support the ability to
    cast any to pandas data frames as needed. The pd df is particularly useful
    for the linear interpolation of colors in visualization.words.

Usage:
    <usage>

"""

import colorsys

import pandas as _pd
import seaborn as _sns

import eri.logging as logging


logger = logging.getLogger(__name__)

BLACK = _pd.Series({'r': 0, 'g': 0, 'b': 0})
AVATAR_LIGHT_GREY = _pd.Series({'r': 175, 'g': 175, 'b': 175})
AVATAR_GREY = _pd.Series({'r': 100, 'g': 100, 'b': 100})
AVATAR_BLUE = _pd.Series({'r': 130, 'g': 220, 'b': 247})
# basically just avatar blue in HSV with the H replace solely by red
AVATAR_RED = _pd.Series({'r': 247, 'g': 130, 'b': 130})

ERI = {
    'dark_blue': _pd.Series({'r': 0, 'g': 45, 'b': 115}),
    'light_blue': _pd.Series({'r': 64, 'g': 124, 'b': 202}),
    'corona_red': _pd.Series({'r': 226, 'g': 35, 'b': 26}),
    'corona_yellow': _pd.Series({'r': 255, 'g': 197, 'b': 1}),
    'white': _pd.Series({'r': 255, 'g': 255, 'b': 255}),
    'black': _pd.Series({'r': 0, 'g': 0, 'b': 0}),
}

def ColorError(Exception):
    def __init__(self, msg, *args, **kwargs):
        logger.error(msg)
        super(self).__init__(msg, *args, **kwargs)


# rgb to ?
def _rgb_to_normed_rgb(c):
    return (_ / 256 for _ in c)


def _rgb_to_hex(c, withHash=True):
    return '{}{:02x}{:02x}{:02x}'.format(
        '#' if withHash else '', c[0], c[1], c[2]
    )


def _rgb_to_hsv(c):
    pass

def _rgb_to_pd(c):
    return _pd.Series(dict(zip('rgb', c)))






# normed_rgb
# hex
# hsv
# cmyk
# pd_rgb
# pd_normed_rgb
# pd_hex
# pd_hsv
# pd_cmyk



# pd to ?

# hex to ?

# hsv to ?

# normalize
def _normalize(c, normType='rgb'):
    try:
        if normType == 'rgb':
            return {k: v / 256 for (k, v) in c.items()}
        else:
            raise ColorError('have not defined')
    except:
        raise ColorError(
            'error normalizing color {} to type {}'.format(c, normType)
        )

def _pd_to_rgb(c):
    return c.r, c.g, c.b


def _pd_to_hex(c):
    return _rgb_to_hex(_pd_to_rgb(c))


def _hex_to_rgb(c):
    c = c.lstrip('#')
    l = len(c)
    return tuple(int(c[i: i + l // 3], 16) for i in range(0, l, l // 3))


def _normed_rgb_to_rgb(c):
    return (_ * 256 for _ in c)


# ----------------------------- #
#   Main routine                #
# ----------------------------- #
