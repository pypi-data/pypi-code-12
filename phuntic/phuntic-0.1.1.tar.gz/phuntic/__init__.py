import datetime
import json
from decimal import Decimal
from pydoc import locate

__version__ = '0.1.0'

__all__ = ['dumps', 'loads', 'PhunticUnknownTypeError']

DICT_TYPES = [dict]

try:
    from frozendict import frozendict

    DICT_TYPES += [frozendict]
except ImportError:
    pass


class PhunticUnknownTypeError(TypeError):
    pass


class PhunticDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, o):
        if '_type' not in o:
            return o

        obj_type = o['_type']
        value = o.get('value', None)

        if obj_type == 'none':
            return None

        if obj_type in ('dict', 'list', 'str'):
            return value

        if obj_type in ('int', 'float', 'set', 'frozenset', 'tuple'):
            return locate(obj_type)(value)

        if obj_type == 'decimal':
            return Decimal(value)

        if obj_type == 'datetime':
            return datetime.datetime.utcfromtimestamp(value)

        if obj_type == 'frozendict':
            return frozendict(value)

        raise ValueError(repr(o) + ' cannot be decoded.')


def wrap_dict(obj):
    return dict(_type=type(obj).__name__, value={k: wrap_object(o) for k, o in obj.items()})


def wrap_list(obj):
    return dict(_type=type(obj).__name__, value=[wrap_object(o) for o in obj])


def wrap_object(obj):
    if obj is None:
        return dict(_type='none')

    elif isinstance(obj, (str, int, float, bool)):
        return dict(_type=type(obj).__name__, value=obj)

    elif isinstance(obj, tuple(DICT_TYPES)):
        return wrap_dict(obj)

    elif isinstance(obj, (list, set, frozenset, tuple)):
        return wrap_list(obj)

    elif isinstance(obj, Decimal):
        return dict(_type='decimal', value=str(obj))

    elif isinstance(obj, datetime.datetime):
        return dict(_type='datetime', value=obj.replace(tzinfo=datetime.timezone.utc).timestamp())

    raise PhunticUnknownTypeError(repr(obj) + " is not phuntic!")


def dumps(obj, **kwargs):
    """Serialize ``obj`` to a JSON formatted ``str``"""
    return json.dumps(wrap_object(obj), **kwargs)


def loads(*args, **kwargs):
    """Deserialize ``s`` (a ``str`` instance containing a JSON document) to a Python object"""
    kwargs['cls'] = kwargs.pop('cls', PhunticDecoder)
    return json.loads(*args, **kwargs)
