# -*- coding: utf-8 -*-
"""
    obscheme.schemameta
    ~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2016 by Thomas Wiebe.
    :license: BSD, see LICENSE for more details.
"""

from obscheme.field import Undefined
from obscheme.schema import NoSchemaImplementedError, factor_invariant_kw


#----------------------------------------------------------------------
def schema_validate_switch(obj):
    return getattr(obj, '__schema_validate__')


#----------------------------------------------------------------------
def requires_schema_validation(obj):
    return getattr(obj, '__schema_validate__', False)


########################################################################
class SchemaValidateSwitch(object):

    #----------------------------------------------------------------------
    def __init__(self, state=True):
        self._validate = state

    #----------------------------------------------------------------------
    def __nonzero__(self):
        return self._validate

    #----------------------------------------------------------------------
    def enable(self):
        self._validate = True

    #----------------------------------------------------------------------
    def disable(self):
        self._validate = False


########################################################################
class SchemaFieldDescriptor(object):

    #----------------------------------------------------------------------
    def __init__(self, name, field):
        self._name = name
        self._field = field
        self._value_attr_name = None
        self._default_value = None
        self._factor_value_holder_attr_name()
        self._factor_default_value()

    #----------------------------------------------------------------------
    def _factor_value_holder_attr_name(self):
        self._value_attr_name = '_{}'.format(self._name)

    #----------------------------------------------------------------------
    def _factor_default_value(self):
        self._default_value = Undefined(self._field)

    #----------------------------------------------------------------------
    def __get__(self, obj, type_):
        return getattr(obj, self._value_attr_name, self._default_value)

    #----------------------------------------------------------------------
    def __set__(self, obj, value):
        if requires_schema_validation(obj):
            self._field.validate(self._name, value)
            self._validate_invariants(obj, value)
        setattr(obj, self._value_attr_name, value)

    #----------------------------------------------------------------------
    def __delete__(self, obj):
        if requires_schema_validation(obj):
            self._validate_invariants(obj, self._default_value)
        delattr(obj, self._value_attr_name)

    #----------------------------------------------------------------------
    def _validate_invariants(self, obj, field_value):
        override_kw = dict()
        override_kw[self._name] = field_value
        for invariant in self._field.invariants:
            kw = factor_invariant_kw(invariant, obj, **override_kw)
            invariant(**kw)


########################################################################
class SchemaMeta(type):
    """
    Enforce schema on modification of object

    Optionally defines __slots__, if __define_slots__ is set to True
    on class.
    """

    #----------------------------------------------------------------------
    def __new__(cls, name, bases, attrs):
        if not '__schema__' in attrs:
            raise NoSchemaImplementedError(name)
        value_holder_attr_names = []
        schema = attrs['__schema__']
        for field_name, field in schema:
            attrs[field_name] = SchemaFieldDescriptor(field_name, field)
            value_holder_attr_names.append('_{}'.format(field_name))
        attrs['__schema_validate__'] = SchemaValidateSwitch()
        if attrs.get('__define_slots__') is True:
            slots = set()
            for base in bases:
                slots.update(getattr(base, '__slots__', []))
            slots.update(attrs.keys())
            slots.update(value_holder_attr_names)
            attrs['__slots__'] = tuple(slots)
        return super(SchemaMeta, cls).__new__(cls, name, bases, attrs)
