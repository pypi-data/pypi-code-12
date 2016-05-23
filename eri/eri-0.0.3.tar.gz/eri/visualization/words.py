#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: words.py
Author: zlamberty
Created: 2016-05-18

Description:
    visualizations of word data -- word clouds, sentence importance plots, etc

Usage:
    <usage>

"""

import lxml.html as _lh
import lxml.html.builder as _lhb
import IPython.core.display as _icd

import eri.logging as _logging
import eri.visualization.colors as _colors


# ----------------------------- #
#   Module Constants            #
# ----------------------------- #

_logger = _logging.getLogger(__name__)


# ----------------------------- #
#   custom errors               #
# ----------------------------- #

class WordVisualizationError(Exception):
    def __init__(self, msg, *args, **kwargs):
        _logger.warning(msg)
        super().__init__(msg, *args, **kwargs)


# ----------------------------- #
#   conversion pipeline funcs   #
# ----------------------------- #

def _wi2ws(wordImp, styleFoo):
    """map styleFoo over the importances in a wordImp iterable

    args:
        wordImp: iterable of (word, importance[, ...]) tuples
        styleFoo: function which maps importance to dictionaries of css-able
            style parameters (e.g. {'font-size': '20px'})

    returns:
        iterable of (word, styleDict) pairs
    """
    return [(wi[0], styleFoo(wi[1])) for wi in wordImp]


def _ws2wd(wordStyle):
    """convert style dicts in a wordStyle into corresponding div elements

    args:
        wordStyle: iterable of (word, styleDict) pairs

    returns:
        iterable of (word, lxml.html div element) pairs

    """
    return [
        _lhb.DIV(
            w + '  ',
            style='; '.join(
                '{k:}: {v:}'.format(k=k, v=v) for (k, v) in s.items()
            ),
            word=w
        )
        for (w, s) in wordStyle
    ]


def _wd2d(wordDiv):
    """cat a list of worddivs into one big happy lxml.html div element

    args:
        wordDiv: iterable of (word, lxml.html div element) pairs

    returns:
        lxml.html div element with len(wordDiv) nested div elements

    """
    rt = _lhb.DIV(id="eri-wordvis-styles")
    for d in wordDiv:
        rt.append(d)
    return rt


# ----------------------------- #
#   common style functions      #
# ----------------------------- #

def _index_finder(val, breaks):
    ileft = -1
    iright = 0
    L = len(breaks)
    while (iright < L) and (val >= breaks[iright]):
        ileft += 1
        iright += 1
    return ileft, iright if iright != L else None


def _linear_scaler(impbreaks, propbreaks):
    """create a styleFoo function which maps importance values to linearly
    segmented ranges

    """
    def f(i):
        if not (impbreaks[0] <= i <= impbreaks[-1]):
            raise WordVisualizationError(
                "imput value {} not between bounds ({}, {})".format(
                    i, impbreaks[0], impbreaks[-1]
                )
            )

        if i == impbreaks[-1]:
            return {p: pb[-1] for (p, pb) in propbreaks.items()}

        # we know which segment of ibreaks is i in?
        ileft, iright = _index_finder(i, impbreaks)
        scale = (i - impbreaks[ileft]) / (impbreaks[iright] - impbreaks[ileft])
        return {
            p: pb[ileft] + (pb[iright] - pb[ileft]) * scale
            for (p, pb) in propbreaks.items()
        }
    return f


def _avatar_styler_factory(impbreaks, propbreaks):
    """_linear_scaler will do the bulk of the lifting, but we need to make some
    modifications (e.g. every div will get an inline format, font sizes need to
    be stringified and have the 'px' added to them)

    """
    firstPass = _linear_scaler(impbreaks, propbreaks)

    def f(i):
        style = firstPass(i)
        style['color'] = style['color'].round().astype('int')
        style['color'] = 'rgb({color.r:}, {color.g}, {color.b})'.format(
            color=style['color']
        )
        style['font-size'] = '{:.2f}px'.format(style['font-size'])
        style['display'] = 'inline'
        return style

    return f


def _avatar_styler_twopoint():
    """two break points in our importance (0, 1) ranking and two colors (black
    and "avatar blue", which I declare to be rgb(130, 220, 247))

    """
    impbreaks = [0, 1]
    propbreaks = {
        'font-size': [2, 40],
        'color': [_colors.BLACK, _colors.AVATAR_BLUE],
    }

    return _avatar_styler_factory(impbreaks, propbreaks)


def _avatar_styler_threepoint():
    """three break points in our importance (0, 0.5, 1) ranking and three colors
    ("avatar red", black and "avatar blue"). Avatar blue is rgb(130, 220, 247)),
    and "avatar red" is just the transposition of r and b values

    """
    impbreaks = [0, 0.5, 1]
    propbreaks = {
        'font-size': [40, 10, 40],
        'color': [_colors.AVATAR_RED, _colors.AVATAR_GREY, _colors.AVATAR_BLUE],
    }

    return _avatar_styler_factory(impbreaks, propbreaks)


AVATAR_STYLER_TWOPOINT = _avatar_styler_twopoint()
AVATAR_STYLER_THREEPOINT = _avatar_styler_threepoint()


# ----------------------------- #
#   Main routines               #
# ----------------------------- #

def sentence_importance(wordImp, styleFoo, retType='lxml'):
    """ use styleFoo to convert wordImp importances into div elements. several
    return types are supported (for different display methods and environments)

    args:
        wordImp: iterable of (word, importance) pairs
        styleFoo: function which maps importance to dictionaries of css-able
            style parameters (e.g. {'font-size': '20px'})
        retType: one of ['lxml', 'str', 'jupy']. 'lxml' will return an lxml.html
            element, 'str' will return the result of lxml.html.tostring on that
            element, and retType will return an ipython/jupyter notebook HTML
            element

    returns:
        one of the three items discussed above in arg `retType`

    """
    x = _wd2d(_ws2wd(_wi2ws(wordImp, styleFoo)))
    if retType == 'lxml':
        return x
    elif retType == 'str':
        return _lh.tostring(x).decode('utf-8')
    elif retType == 'jupy':
        return _icd.HTML(_lh.tostring(x).decode('utf-8'))
    else:
        raise WordVisualizationError(
            "return type {} is not defined".format(retType)
        )
