#
# Copyright (c) 2015, Prometheus Research, LLC
#


import collections
import json

import yaml

from six import text_type, add_metaclass


__all__ = (
    'get_json',
    'get_yaml',

    'OrderedDict',
    'SortedDict',
    'TypedSortedDict',
    'DefinedOrderDict',
    'TypedDefinedOrderDict',

    'InstrumentReference',
    'Descriptor',
)


def get_json(data, pretty=False, **kwargs):
    """
    A convenience wrapper around ``json.dumps`` that respects the ordering of
    keys in classes like ``OrderedDict``, ``SortedDict``, and
    ``DefinedOrderDict``.

    :param data: the object to encode in JSON
    :param pretty:
        whether or not the output should be indented in human-friendly ways
    :type pretty: boolean
    :returns: a JSON-encoded string
    """

    kwargs['ensure_ascii'] = False
    kwargs['sort_keys'] = False

    if pretty:
        kwargs['indent'] = 2
        kwargs['separators'] = (',', ': ')

    return json.dumps(data, **kwargs)


def get_yaml(data, pretty=False, **kwargs):
    """
    A convenience wrapper around ``yaml.dump`` that respects the ordering of
    keys in classes like ``OrderedDict``, ``SortedDict``, and
    ``DefinedOrderDict``.

    :param data: the object to encode in YAML
    :param pretty:
        whether or not the output should be indented in human-friendly ways
    :type pretty: boolean
    :returns: a YAML-encoded string
    """

    kwargs['Dumper'] = OrderedDumper
    kwargs['allow_unicode'] = True

    if pretty:
        kwargs['default_flow_style'] = False

    return yaml.dump(data, **kwargs).rstrip()


class OrderedDumper(yaml.Dumper):
    pass


def unicode_representer(dumper, ustr):
    return dumper.represent_scalar(
        'tag:yaml.org,2002:str',
        ustr,
    )


OrderedDumper.add_representer(text_type, unicode_representer)


def dict_representer(dumper, data):
    return dumper.represent_mapping(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        list(data.items())
    )


class OrderedDumperMetaclass(type):
    def __init__(cls, name, bases, dct):  # noqa
        super(OrderedDumperMetaclass, cls).__init__(name, bases, dct)
        OrderedDumper.add_representer(cls, dict_representer)


@add_metaclass(OrderedDumperMetaclass)
class OrderedDict(collections.OrderedDict):
    """
    A functional equivalent to ``collections.OrderedDict``.
    """

    pass


@add_metaclass(OrderedDumperMetaclass)
class SortedDict(dict):
    """
    A dictionary class that sorts its keys alphabetically.
    """

    def get_keys(self):
        return sorted(super(SortedDict, self).keys())

    def keys(self):
        return self.get_keys()

    def __iter__(self):
        return iter(self.get_keys())

    def items(self):
        return [
            (key, self[key])
            for key in self.get_keys()
        ]

    def iteritems(self):
        for key in self.get_keys():
            yield (key, self[key])


class TypedSortedDict(SortedDict):
    """
    A variety of the ``SortedDict`` class that automatically casts the value of
    all keys to the type specified on the ``subtype`` property.
    """

    #: The type to cast all values in the dictionary to.
    subtype = None

    def __init__(self, obj=None):
        super(TypedSortedDict, self).__init__(obj or {})
        for key in self:
            self[key] = self[key]

    def __setitem__(self, key, value):
        if self.subtype:
            # pylint: disable=E1102
            value = self.subtype(value)
        super(TypedSortedDict, self).__setitem__(key, value)


class DefinedOrderDict(SortedDict):
    """
    A dictionary class that orders its keys according to its ``order``
    property (any unnamed keys are then sorted alphabetically).
    """

    #: A list of key names in the order you want them to be output.
    order = []

    def get_keys(self):
        existing_keys = super(DefinedOrderDict, self).get_keys()
        keys = []
        for key in self.order:
            if key in existing_keys:
                keys.append(key)
        for key in existing_keys:
            if key not in self.order:
                keys.append(key)
        return keys


class TypedDefinedOrderDict(DefinedOrderDict):
    """
    A variety of the ``DefinedOrderDict`` class that provides for the automatic
    casting of values in the dictionary based on their key. This conversion is
    driven by the ``key_types`` property. E.g.::

        key_types = {
            'foo': SortedOrderDict,
            'bar': [SortedOrderDict],
        }
    """

    #: The mapping of key names to types. To indicate that the key should
    #: contain a list of casted values, place the type in a list with one
    # element.
    key_types = {}

    def __init__(self, obj=None):
        super(TypedDefinedOrderDict, self).__init__(obj or {})
        for key in self.key_types:
            if key in self:
                # Force an invokation of our __setitem__
                self[key] = self[key]

    def __setitem__(self, key, value):
        if key in self.key_types:
            type_ = self.key_types[key]
            if isinstance(type_, list):
                value = [
                    type_[0](val)
                    for val in value
                ]
            else:
                value = type_(value)
        super(TypedDefinedOrderDict, self).__setitem__(key, value)


class InstrumentReference(TypedDefinedOrderDict):
    order = [
        'id',
        'version',
    ]

    key_types = {
        'version': str,
    }


class Descriptor(TypedDefinedOrderDict):
    order = [
        'id',
        'text',
        'help',
        'audio',
    ]

    key_types = {
        'id': str,
        'text': SortedDict,
        'help': SortedDict,
        'audio': SortedDict,
    }

