#
# Copyright (c) 2015, Prometheus Research, LLC
#


from .common import SortedDict, TypedDefinedOrderDict, InstrumentReference, \
    Descriptor


__all__ = (
    'Interaction',
)


class StepOptions(TypedDefinedOrderDict):
    order = [
        'fieldId',
        'text',
        'error',
        'enumerations',
    ]

    key_types = {
        'text': SortedDict,
        'error': SortedDict,
        'enumerations': [Descriptor],
    }


class Step(TypedDefinedOrderDict):
    order = [
        'type',
        'options',
    ]

    key_types = {
        'options': StepOptions,
    }


class TimeoutDetails(TypedDefinedOrderDict):
    order = [
        'threshold',
        'text',
    ]

    key_types = {
        'text': SortedDict,
    }


class Timeout(TypedDefinedOrderDict):
    order = [
        'warn',
        'abort',
    ]

    key_types = {
        'warn': TimeoutDetails,
        'abort': TimeoutDetails,
    }


class Interaction(TypedDefinedOrderDict):
    order = [
        'instrument',
        'meta',
        'defaultLocalization',
        'defaultTimeout',
        'steps',
    ]

    key_types = {
        'instrument': InstrumentReference,
        'meta': SortedDict,
        'defaultTimeout': Timeout,
        'steps': [Step],
    }

