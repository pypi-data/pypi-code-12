#
# Copyright (c) 2015, Prometheus Research, LLC
#


from .common import SortedDict, TypedDefinedOrderDict, InstrumentReference


__all__ = (
    'CalculationSet',
)


class Calculation(TypedDefinedOrderDict):
    order = [
        'id',
        'description',
        'type',
        'identifiable',
        'method',
        'options',
    ]

    key_types = {
        'options': SortedDict,
    }


class CalculationSet(TypedDefinedOrderDict):
    order = [
        'instrument',
        'meta',
        'calculations',
    ]

    key_types = {
        'instrument': InstrumentReference,
        'meta': SortedDict,
        'calculations': [Calculation],
    }

