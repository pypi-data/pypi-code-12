#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: string.py
Author: zlamberty
Created: 2016-02-18

Description:
    ERI data-science-specific string functions (think string distance utilities)

Usage:
    <usage>

"""

import collections as _collections
import functools as _functools
import itertools as _itertools
import jellyfish as _jellyfish
import numpy as _np
import pandas as _pd

import eri.logging as _logging


# ----------------------------- #
#   Module Constants            #
# ----------------------------- #

_logger = _logging.getLogger(__name__)


# ----------------------------- #
#   errors                      #
# ----------------------------- #

class EriStringError(Exception):
    def __init__(self, msg, *args, **kwargs):
        _logger.error(msg)
        super().__init__(*args, **kwargs)


# ----------------------------- #
#   string distant utils        #
# ----------------------------- #

def _pairwise_distance_generator(wordlist, distfunc, minThresh=None,
                                 maxThresh=None, filterfunc=None,
                                 symmetric=True, *funcargs, **funckwargs):
    """generator of distances for word pairs in wordlist, where distance is
    measured by func

    Note: *IT IS ASSUMED THAT THE DISTANCE FUNCTION IS SYMMETRIC*. The returned
        iterable will run over *combinations*, not products, of the word pairs.
        This means you may need to duplicate certain values (e.g. [w1, w2, val]
        is returned, but [w2, w1, val] is not)

    args:
        wordlist: (iterable) an iterable of strings
        distfunc: (func) the function which measures distance between word pairs
        minThresh: (None or float) if supplied, only return pairs with distfunc
            values <= to minThresh
        maxThresh: (None or float) if supplied, only return pairs with distfunc
            values >= to maxThresh
        filterfunc: (None or func) if you want to do some filtering *other* than
            minThresh <= distfunc(w1, w2) <= maxThresh, provide a function which
            takes a distfunc(w1, w2) value and returns a bool indicating whether
            or not that should be yielded
        *funcargs: passed to func
        *funckwargs: passed to func

    yields:
        a tuple (word1, word2, funcdist)

    raises:
        EriStringError: if you provide either thresh value and filterfunc, there
            is no clear path forward.

    """
    if (minThresh or maxThresh) and filterfunc:
        raise EriStringError(
            "You have provided both a boundary threshhold value and filterfunc; "
            "only one is allowed"
        )

    for (word1, word2) in _itertools.combinations(wordlist, r=2):
        x = distfunc(word1, word2, *funcargs, **funckwargs)
        shouldYield = all([
            (minThresh is None) or (minThresh <= x),
            (maxThresh is None) or (x <= maxThresh),
            (filterfunc is None) or filterfunc(x),
        ])
        if shouldYield:
            yield (word1, word2, x)


def levenshtein(wordlist, thresh=None):
    """turn a list of words into a generator of (word1, word2, levenshtein dist)
    tuples

    args:
        wordlist: (iterable) an iterable of word strings
        thresh: (None or int) if provided, only return values less than or equal
            to thresh

    returns:
        a generator of (word1, word2, levDist) tuples

    raises:
        EriStringError

    """
    _logger.info("calculating pairwise levenshtein distances")
    return _pairwise_distance_generator(
        wordlist=wordlist,
        distfunc=_jellyfish.levenshtein_distance,
        maxThresh=thresh
    )


def jaro_winkler(wordlist, vectorized=False, minThresh=None, normThresh=None):
    """turn a list of words (or word-like tuples) into a generator of
    (word1, word2, levenshtein dist) tuples. The default behavior is to
    calculate the jaro-winkler distance of any combination of words in wordlist,
    but if vectorized is True it will assume the elements of wordlist are
    actually iterables of words and calculate the vector of jaro-winkler
    distances (this is specifically targeted for calculating
    (firstname, lastname) pair similarities).

    We also offer two possible threshold options; one being to include only
    options where the distance (or all distances, for vectorized) is greater
    than or equal to minThresh, and another being where the magnitude of the
    distance vector is >= normThresh. normThresh is not supported for
    non-vectorized calls

    args:
        wordlist: (iterable) an iterable of word strings
        vectorized: (bool) whether or not the elements of wordlist are word
            strings or iterables of word strings (also, determines the form of
            the distance outputed)
        minThresh: (None or int) if provided, a minimum distance value which a
            given tuple's distance (or all distances in its vector) must exceed
            in order to be yielded
        normThresh: (None or int) if provided, a minimum distance value
            magnitude which a given tuple's distance vector must exceed in
            order to be yielded. Note: only allowed for vectorized calls

    returns:
        a generator of (word1, word2, jwDist) tuples

    raises:
        EriStringError

    """
    _logger.info("calculating pairwise jaro-winkler distances")

    # can't specify both minthresh and normthresh
    if minThresh and normThresh:
        raise EriStringError(
            "You can pick minThresh or normThresh but not both"
        )

    # vectorized logixs
    if vectorized:
        _logger.debug("calculating a vectorized jaro winkler distance")
        jw = _jw_vector
        filterfunc = None

        if minThresh:
            _logger.debug("minimum threshold set to {}".format(minThresh))
            filterfunc=lambda dvec: all(d >= minThresh for d in dvec)
        elif normThresh:
            _logger.debug(
                "minimum magnitude threshold set to {}".format(normThresh)
            )
            filterfunc=lambda dvec: _np.sqrt(_np.square(dvec).sum()) >= normThresh

    else:
        _logger.debug(
            "calculating the normal (non-vectorize) jaro winkler distance"
        )
        jw = _jellyfish.jaro_winkler
        filterfunc = None

        if minThresh:
            _logger.debug("minimum threshold set to {}".format(minThresh))
            filterfunc=lambda d: d >= minThresh
        elif normThresh:
            raise EriStringError(
                "normThresh is meaningless for non-vectorized wordlists"
            )

    return _pairwise_distance_generator(
        wordlist=wordlist,
        distfunc=jw,
        filterfunc=filterfunc
    )


def _jw_vector(wordvec1, wordvec2):
    """slight tweak on regular jaro_winkler to return a list of jaro winkler
    values for two (assumed to be matching length) vectors of word strings

    args:
        wordvec1: (iterable of strings) multiple words
        wordvec2: (iterable of strings) multiple words

    returns:
        a list of jaro winkler distances for the zipped wordvec1/2 lists

    raises:
        None

    """
    return [
        _jellyfish.jaro_winkler(word1, word2)
        for (word1, word2) in zip(wordvec1, wordvec2)
    ]
