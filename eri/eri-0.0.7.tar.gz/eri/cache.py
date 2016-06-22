#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: cache.py
Author: zlamberty
Created: 2016-03-04

Description:
    common caching functions

Usage:
    <usage>

"""

import datetime as _datetime
import functools as _functools
import os as _os
import pickle as _pickle

import eri.logging as _logging


# ----------------------------- #
#   Module Constants            #
# ----------------------------- #

_logger = _logging.getLogger(__name__)


# ----------------------------- #
#   Main routine                #
# ----------------------------- #

def file_cache(filename, cachetype='pkl'):
    """decorator for functions whose return values we can cache as a file. Note
    that filename is static, so it doesn't depend on the parameters -- this is
    intentional. The main intent is functions which don't change frequently
    and don't depend on the parameters (e.g. calculations made on relatively
    static web data); for more rapidly changing data or multiple parameters I
    recommend the much more feature-rich functools.lru_cache

    args:
        filename: (str file uri) where data will be saved. Note: I will
            automatically format this string with the current datetime, so if
            you want to have a timestamp on your file include it in this param
        cachetype: (string) enumerated cache types determine what the output is,
            not the extension (i.e. 'myfile.csv' with cachetype 'pkl' will
            output a pickle formatted file with a csv extension -- probably a
            bad idea right? maybe don't do that)

    """
    filename = filename.format(_datetime.datetime.now())
    if cachetype == 'pkl':
        return _pkl_file_cache(filename)
    else:
        raise NotImplementedError(
            "cache type {} is not yet defined".format(cachetype)
        )

def _pkl_file_cache(filename):
    """pickle function results and use as cache. More details in file_cache

    args:
        filename: (str file uri) where data will be saved. Note: I will
            automatically format this string with the current datetime, so if
            you want to have a timestamp on your file include it in this param

    """
    fileExists = _os.access(filename, _os.R_OK)

    # build a function which returns a decorator
    def fwrapper(f):
        @_functools.wraps(f)
        def fnew(forcerefresh=False, *args, **kwargs):
            # make sure forcerefresh was not an arg already
            if 'forcerefresh' in kwargs:
                err = "wrapped function uses 'forcerefresh' as a variable"
                _logger.error(err)
                _logger.debug("wrapper assumes it can add that as a new param")
                raise ValueError(err)
            # add forcerefresh as a docstring value
            f.__doc__ = f.__doc__.replace(
                'args:\n        ',
                'args:\n        forcerefresh: (bool) invalidate cache\n        ',
            )
            if forcerefresh or not fileExists:
                x = f(*args, **kwargs)
                with open(filename, 'wb') as fout:
                    _pickle.dump(x, fout)
                return x
            else:
                _logger.debug("caching method is 'pkl'")
                _logger.debug('using cached value from file {}'.format(filename))
                with open(filename, 'rb') as fin:
                    return _pickle.load(fin)
        return fnew
    return fwrapper
