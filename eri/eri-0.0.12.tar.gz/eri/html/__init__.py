#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: html.py
Author: zlamberty
Created: 2016-01-21

Description:
    html helper tools / wrappers

Usage:
    <usage>

"""

import functools as _functools
import os as _os
import pickle as _pickle

import eri.logging as _logging

import lxml.html as _html
import requests as _requests

# ----------------------------- #
#   Module Constants            #
# ----------------------------- #

_logger = _logging.getLogger(__name__)


# ----------------------------- #
#   Main routine                #
# ----------------------------- #

def html_local_cache(dirname):
    def parameterized_decorator(foo):
        @_functools.wraps(foo)
        def fnew(url=None, forcerefresh=False, *args, **kwargs):
            if url is None:
                _logger.debug("no argument named 'url', no local caching is performed")
                return foo(*args, **kwargs)
            else:
                localfile = _os.path.join(
                    dirname, '{}.pkl'.format(_os.path.basename(url))
                )
                if forcerefresh or not _os.access(localfile, _os.R_OK):
                    x = foo(*args, **kwargs)
                    with open(localfile, 'wb') as f:
                        _pickle.dump(x, f)
                    return x
                else:
                    with open(localfile, 'rb') as f:
                        return _pickle.load(f)
        return fnew

    return parameterized_decorator


@html_local_cache(dirname=".")
def _testget(url=None):
    return _html.fromstring(_requests.get(url).text)
