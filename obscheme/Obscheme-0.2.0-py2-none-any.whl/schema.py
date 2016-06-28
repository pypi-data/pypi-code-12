# -*- coding: utf-8 -*-
"""
    obscheme.schema
    ~~~~~~~~~~~~~~~

    :copyright: (c) 2016 by Thomas Wiebe.
    :license: BSD, see LICENSE for more details.
"""

from functools import wraps
import inspect

from obscheme.exceptions import InvariantError
from obscheme.field import Field
from obscheme.util import InitializationEnforcer


########################################################################
class NoSchemaImplementedError(Exception):

    #----------------------------------------------------------------------
    def __init__(self, cls_name):
        self.cls_name = cls_name

    #----------------------------------------------------------------------
    def __str__(self):
        return u'Class {} does not implement a schema'.format(self.cls_name)


#----------------------------------------------------------------------
def schema_of(cls):
    try:
        return getattr(cls, '__schema__')
    except AttributeError:
        raise NoSchemaImplementedError(cls.__name__)


#----------------------------------------------------------------------
def invariant(func):
    @wraps(func)
    def wrapper(*a, **kw):
        result = func(*a, **kw)
        if result is not None:
            if isinstance(result, basestring):
                message = result
            else:
                message = func.im_func.func_name
            raise InvariantError(message)
        return result

    wrapper.is_invariant = True
    wrapper.invariant_field_names = tuple(inspect.getargspec(func).args[1:])
    return wrapper


#----------------------------------------------------------------------
def is_invariant(func):
    return getattr(func, 'is_invariant', False)


#----------------------------------------------------------------------
def factor_invariant_kw(func, obj, **override_kw):
    kw = dict()
    for field_name in func.invariant_field_names:
        value = getattr(obj, field_name)
        kw[field_name] = value
    kw.update(override_kw)
    return kw


########################################################################
class Schema(object):

    _fields_index = InitializationEnforcer()

    #----------------------------------------------------------------------
    def __init__(self):
        self._build_fields_index()
        self._register_invariants()

    #----------------------------------------------------------------------
    def _build_fields_index(self):
        self._fields_index = dict([
            (attr_name, getattr(self, attr_name))
            for attr_name in dir(self)
            if not attr_name.startswith('_') and
            isinstance(getattr(self, attr_name), Field)])

    #----------------------------------------------------------------------
    def _register_invariants(self):
        for attr_name in dir(self):
            invariant = getattr(self, attr_name)
            if not callable(invariant):
                continue
            if not is_invariant(invariant):
                continue
            for field_name in invariant.invariant_field_names:
                field = getattr(self, field_name)
                field.add_invariant(invariant)

    #----------------------------------------------------------------------
    def __iter__(self):
        for name, value in self._fields_index.items():
            yield name, value
        raise StopIteration()

    #----------------------------------------------------------------------
    def __contains__(self, name):
        return name in self._fields_index

    #----------------------------------------------------------------------
    def validate(self, obj):
        invariants = set()
        for name, field in self:
            value = getattr(obj, name)
            if field.is_defined(value):
                field.validate(name, value)
            invariants.update(field.invariants)
        for invariant in invariants:
            invariant(obj)
