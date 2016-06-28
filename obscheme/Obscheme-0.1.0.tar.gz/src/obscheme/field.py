# -*- coding: utf-8 -*-
"""
    obscheme.field
    ~~~~~~~~~~~~~~

    :copyright: (c) 2016 by Thomas Wiebe.
    :license: BSD, see LICENSE for more details.
"""

from abc import ABCMeta, abstractmethod


########################################################################
class Undefined(object):

    #----------------------------------------------------------------------
    def __init__(self, field):
        self.field = field

    #----------------------------------------------------------------------
    def __getattr__(self, name):
        """Allows access to field attributes and methods"""
        if not name.startswith('_'):
            return getattr(self.field, name)
        raise AttributeError(name)

    #----------------------------------------------------------------------
    def __repr__(self):
        return u'Undefined<{!r}>'.format(self.field.__class__.__name__)


########################################################################
class Field(object):
    __metaclass__ = ABCMeta

    #----------------------------------------------------------------------
    def __init__(self):
        self._invariants = []

    #----------------------------------------------------------------------
    def add_invariant(self, invariant):
        self._invariants.append(invariant)

    #----------------------------------------------------------------------
    def invariants(self):
        return tuple(self._invariants)

    #----------------------------------------------------------------------
    def is_defined(self, value):
        return not isinstance(value, Undefined)

    #----------------------------------------------------------------------
    def validate(self, name, value):
        self._validate(name, value)

    #----------------------------------------------------------------------
    @abstractmethod
    def _validate(self, name, value):
        pass

    #----------------------------------------------------------------------
    def __repr__(self):
        return u'{}()'.format(self.__class__.__name__)
