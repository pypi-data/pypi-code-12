#
# Copyright (c) 2015, Prometheus Research, LLC
#


from .common import SortedDict, TypedSortedDict, TypedDefinedOrderDict, \
    InstrumentReference, Descriptor


__all__ = (
    'Form',
)


class Event(TypedDefinedOrderDict):
    order = [
        'trigger',
        'action',
        'targets',
        'options',
    ]

    key_types = {
        'options': SortedDict,
    }


class Widget(TypedDefinedOrderDict):
    order = [
        'type',
        'options',
    ]

    key_types = {
        'options': SortedDict,
    }


class ElementOptions(TypedDefinedOrderDict):
    order = [
        'fieldId',
        'text',
        'help',
        'error',
        'audio',
        'enumerations',
        'questions',
        'rows',
        'widget',
        'events',
    ]

    key_types = {
        'text': SortedDict,
        'help': SortedDict,
        'error': SortedDict,
        'audio': SortedDict,
        'enumerations': [Descriptor],
        'rows': [Descriptor],
        'widget': Widget,
        'events': [Event],
    }

ElementOptions.key_types['questions'] = [ElementOptions]


class Element(TypedDefinedOrderDict):
    order = [
        'type',
        'tags',
        'options',
    ]

    key_types = {
        'options': ElementOptions,
    }


class Page(TypedDefinedOrderDict):
    order = [
        'id',
        'elements',
    ]

    key_types = {
        'elements': [Element],
    }


class Parameter(TypedDefinedOrderDict):
    order = [
        'type',
    ]


class ParameterCollection(TypedSortedDict):
    subtype = Parameter


class Form(TypedDefinedOrderDict):
    order = [
        'instrument',
        'meta',
        'defaultLocalization',
        'title',
        'pages',
        'parameters',
    ]

    key_types = {
        'instrument': InstrumentReference,
        'meta': SortedDict,
        'title': SortedDict,
        'pages': [Page],
        'parameters': ParameterCollection,
    }

