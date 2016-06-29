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
    @property
    def authoritative_field(self):
        return self.field.authoritative_field

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
    @property
    def invariants(self):
        return tuple(self._invariants)

    #----------------------------------------------------------------------
    def is_defined(self, value):
        return not isinstance(value, Undefined)

    #----------------------------------------------------------------------
    @property
    def authoritative_field(self):
        return self

    #----------------------------------------------------------------------
    @abstractmethod
    def validate(self, name, value):
        pass

    #----------------------------------------------------------------------
    def __repr__(self):
        return u'{}()'.format(self.__class__.__name__)
