#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import copy
from ec3 import compat, exceptions


class AttrDict(dict):
    def __getattr__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        elif key in self:
            return self[key]
        raise AttributeError(key)


class ConstantDict(dict):
    def __init__(self, **kwargs):
        for key, val in compat.iteritems(kwargs):
            super(ConstantDict, self).__setitem__(key, val)

    def __getitem__(self, key):
        val = super(ConstantDict, self).__getitem__(key)
        if val is None:
            return val
        elif hasattr(val, '__call__'):
            return val()
        elif isinstance(val, (basestring, int, float, tuple)):
            # builtin immutable type
            return val
        return copy.deepcopy(val)

    def ___iteritems(self):
        for key in self.keys():
            yield key, self[key]

    def items(self):
        if compat.IS_PYTHON_2:
            return list(self.___iteritems())
        return self.___iteritems()

    if compat.IS_PYTHON_2:
        def iteritems(self):
            return self.___iteritems()

    def __setitem__(self, key, val):
        raise exceptions.UnsupportedMethod("ConstantDict is immutable.")


def is_iterator(x):
    return hasattr(x, 'next') and hasattr(x.next, '__call__')
