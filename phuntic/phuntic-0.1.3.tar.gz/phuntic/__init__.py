import datetime
import json
from decimal import Decimal
from pydoc import locate

__version__ = '0.1.3'

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

        return _unwrap_object(o, nested=False)


def _unwrap_object(obj, nested=False):
    obj_type = obj['_type']
    value = obj.get('value', None)

    if obj_type == 'none':
        return None

    if obj_type in ('bool', 'str', 'int', 'float'):
        return locate(obj_type)(value)

    if obj_type == 'decimal':
        return Decimal(value)

    if obj_type == 'datetime':
        return datetime.datetime.utcfromtimestamp(value)

    if obj_type in ('list', 'dict'):
        return locate(obj_type)(unwraps(value)) if nested else value

    if obj_type in ('set', 'frozenset', 'tuple'):
        if nested:
            value = unwraps(value)
        return locate(obj_type)(value)

    if obj_type == 'frozendict':
        if nested:
            value = unwraps(value)
        return frozendict(value)

    raise ValueError(repr(obj) + ' cannot be decoded.')


def unwraps(obj):
    if isinstance(obj, dict):
        if '_type' not in obj:
            return {k: unwraps(o) for k, o in obj.items()}
        return _unwrap_object(obj, nested=True)

    elif isinstance(obj, list):
        return [unwraps(o) for o in obj]

    raise ValueError(repr(obj) + ' is unknown')


def wraps(obj):
    if obj is None:
        return dict(_type='none')

    elif isinstance(obj, (str, int, float, bool)):
        return dict(_type=type(obj).__name__, value=obj)

    elif isinstance(obj, tuple(DICT_TYPES)):
        return dict(_type=type(obj).__name__, value={k: wraps(o) for k, o in obj.items()})

    elif isinstance(obj, (list, set, frozenset, tuple)):
        return dict(_type=type(obj).__name__, value=[wraps(o) for o in obj])

    elif isinstance(obj, Decimal):
        return dict(_type='decimal', value=str(obj))

    elif isinstance(obj, datetime.datetime):
        return dict(_type='datetime', value=obj.replace(tzinfo=datetime.timezone.utc).timestamp())

    raise PhunticUnknownTypeError(repr(obj) + " is not phuntic!")


def dumps(obj, **kwargs):
    """Serialize ``obj`` to a JSON formatted ``str``"""
    return json.dumps(wraps(obj), **kwargs)


def loads(*args, **kwargs):
    """Deserialize ``s`` (a ``str`` instance containing a JSON document) to a Python object"""
    kwargs['cls'] = kwargs.pop('cls', PhunticDecoder)
    return json.loads(*args, **kwargs)
