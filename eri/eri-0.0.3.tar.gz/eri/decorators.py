#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: decorators.py
Author: zlamberty
Created: 2016-02-11

Description:
    useful function and class decorators

Usage:
    <usage>

"""

import functools
import lxml

import eri.logging as _logging


# ----------------------------- #
#   Module Constants            #
# ----------------------------- #

_logger = _logging.getLogger(__name__)


# ----------------------------- #
#   wrappers                    #
# ----------------------------- #

def loglength(f):
    @functools.wraps(f)
    def fnew(*args, **kwargs):
        x = f(*args, **kwargs)
        _logger.info('function {} returns {} items'.format(f.__name__, len(x)))
        return x

    return fnew


def _xmllogwrap(level):
    return lambda node: getattr(logger, level)(
        lxml.etree.tostring(node, pretty_print=True)
    )


def xmllog(level='info'):
    """this decorator will catch any error raise by the wrapped function and
    print the xml objects used to call that function (can be very useful for
    debugging lxml parsing functions)

    args:
        level: the logger level to which we want all logged xml strings to be
            written

    returns:
        decorator function (which subsequently decorates the following function)

    """
    try:
        logfunc = _xmllogwrap(level)
    except AttributeError:
        raise ValueError("not a vaid logging level : {}".format(level))
    except:
        raise

    def fwrapper(f):
        @functools.wraps(f)
        def fnew(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except:
                for arg in args:
                    if isinstance(arg, lxml.html.HtmlElement):
                        logfunc(arg)
                for (k, v) in kwargs.items():
                    if isinstance(v, lxml.html.HtmlElement):
                        logfunc(v)
                raise

        return fnew

    return fwrapper
