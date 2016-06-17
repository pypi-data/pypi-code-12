#
# Copyright (c) 2015, Prometheus Research, LLC
#


from .common import SortedDict, TypedSortedDict, DefinedOrderDict, \
    TypedDefinedOrderDict


__all__ = (
    'MatrixRow',
    'BoundConstraint',
    'InstrumentField',
    'InstrumentType',
    'InstrumentTypeCollection',
    'Instrument',
)


class MatrixRow(DefinedOrderDict):
    order = [
        'id',
        'description',
        'required',
    ]


class BoundConstraint(DefinedOrderDict):
    order = [
        'min',
        'max',
    ]


class InstrumentField(DefinedOrderDict):
    order = [
        'id',
        'description',
        'type',
        'required',
        'identifiable',
        'annotation',
        'explanation',
    ]

    def __init__(self, field=None):
        super(InstrumentField, self).__init__(field or {})
        if 'type' in self:
            self['type'] = self['type']

    def __setitem__(self, key, value):
        if key == 'type' and isinstance(value, dict):
            value = InstrumentType(value)
        super(InstrumentField, self).__setitem__(key, value)


class InstrumentType(TypedDefinedOrderDict):
    order = [
        'base',
        'range',
        'length',
        'pattern',
        'enumerations',
        'record',
        'columns',
        'rows',
    ]

    key_types = {
        'record': [InstrumentField],
        'columns': [InstrumentField],
        'length': BoundConstraint,
        'range': BoundConstraint,
        'rows': [MatrixRow],
        'enumerations': SortedDict,
    }


class InstrumentTypeCollection(TypedSortedDict):
    subtype = InstrumentType


class Instrument(TypedDefinedOrderDict):
    order = [
        'id',
        'version',
        'title',
        'description',
        'meta',
        'types',
        'record',
    ]

    key_types = {
        'version': str,
        'meta': SortedDict,
        'types': InstrumentTypeCollection,
        'record': [InstrumentField],
    }

