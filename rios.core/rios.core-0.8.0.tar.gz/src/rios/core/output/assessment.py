#
# Copyright (c) 2015, Prometheus Research, LLC
#


from six import string_types

from .common import SortedDict, TypedSortedDict, TypedDefinedOrderDict, \
    InstrumentReference


__all__ = (
    'Assessment',
)


class Value(TypedDefinedOrderDict):
    order = [
        'value',
        'annotation',
        'explanation',
        'meta',
    ]

    key_types = {
        'meta': SortedDict,
    }

    def __init__(self, value=None):
        super(Value, self).__init__(value or {})
        if 'value' in self:
            self['value'] = self['value']

    def __setitem__(self, key, value):
        if key == 'value':
            if isinstance(value, dict):
                value = ValueCollectionMapping(value)
            elif isinstance(value, list):
                if not isinstance(value[0], string_types):
                    value = [
                        ValueCollection(v)
                        for v in value
                    ]
        super(Value, self).__setitem__(key, value)


class ValueCollection(TypedSortedDict):
    subtype = Value


class ValueCollectionMapping(TypedSortedDict):
    subtype = ValueCollection


class Assessment(TypedDefinedOrderDict):
    order = [
        'instrument',
        'meta',
        'values',
    ]

    key_types = {
        'instrument': InstrumentReference,
        'meta': SortedDict,
        'values': ValueCollection
    }

