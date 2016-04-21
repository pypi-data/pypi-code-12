"""A collection of utility methods used by various parts of the bidon package."""
import json
import re
import sys
from contextlib import contextmanager
from uuid import UUID

from . import convert
from . import date

_JSON_DEFAULTS = []


# pylint: disable=invalid-name
try_parse_int = convert.try_wrapper(convert.to_int)
try_parse_float = convert.try_wrapper(convert.to_float)
try_parse_decimal = convert.try_wrapper(convert.to_decimal)
try_parse_date = convert.try_wrapper(date.parse_date)
try_parse_time = convert.try_wrapper(date.parse_time)
try_parse_datetime = convert.try_wrapper(date.parse_datetime)
# pylint: enable=invalid-name


IS_UUID_RE = re.compile(r"^[a-z0-9]{8}(-[a-z0-9]{4}){3}-[a-z0-9]{12}$")
def is_uuid(val):
  """Checks whether the value is either an instance of UUID, or if it matches a uuid regex.

  :val: the value to check"""
  return val and (isinstance(val, UUID) or IS_UUID_RE.match(val) != None)


def exclude(source, keys, *, transform=None):
  """Returns a dictionary excluding keys from a source dictionary.

  :source: a dictionary
  :keys: a set of keys, or a predicate function that accepting a key
  :transform: a function that transforms the values
  """
  check = keys if callable(keys) else lambda key: key in keys
  return {key: transform(source[key]) if transform else source[key]
          for key in source if not check(key)}


def pick(source, keys, *, transform=None):
  """Returns a dictionary including only specified keys from a source dictionary.

  :source: a dictionary
  :keys: a set of keys, or a predicate function that accepting a key
  :transform: a function that transforms the values
  """
  check = keys if callable(keys) else lambda key: key in keys
  return {key: transform(source[key]) if transform else source[key]
          for key in source if check(key)}


def register_json_default(pred, convert_):
  """Register a predicate and converter function for json defaults.

  The registered functions are searched in order they are registered.

  :pred: a function that returns true when a particular value should be converted using :convert_:
  :convert_: a function that transforms a value to one that can be included in JSON
  """
  _JSON_DEFAULTS.append((pred, convert_))


def json_default(obj):
  """Convert an object to JSON, via the defaults set with register_json_default.

  :obj: the object to convert
  """
  for default in _JSON_DEFAULTS:
    if default[0](obj):
      return default[1](obj)
  raise TypeError(repr(obj) + " is not JSON serializable")


def to_json(obj, pretty=False):
  """Converts an object to JSON, using the defaults specified in register_json_default.

  :obj: the object to convert to JSON
  :pretty: if True, extra whitespace is added to make the output easier to read
  """
  sort_keys = False
  indent = None
  separators = (",", ":")

  if isinstance(pretty, tuple):
    sort_keys, indent, separators = pretty
  elif pretty is True:
    sort_keys = True
    indent = 2
    separators = (", ", ": ")

  return json.dumps(obj, sort_keys=sort_keys, indent=indent, separators=separators,
                    default=json_default)


def has_value(obj, name):
  """A flexible method for getting values from objects by name.

  returns:
  - obj is None: (False, None)
  - obj is dict: (name in obj, obj.get(name))
  - obj hasattr(name): (True, getattr(obj, name))
  - else: (False, None)

  :obj: the object to pull values from
  :name: the name to use when getting the value
  """
  if obj is None:
    return (False, None)
  elif isinstance(obj, dict):
    return (name in obj, obj.get(name))
  elif hasattr(obj, name):
    return (True, getattr(obj, name))
  elif hasattr(obj, "__getitem__") and hasattr(obj, "__contains__") and name in obj:
    return (True, obj[name])
  else:
    return (False, None)


def get_value(obj, name, fallback=None):
  """Calls through to has_value. If has_value[0] is True, return has_value[1] otherwise returns
  fallback() if fallback is callable, else just fallback.

  :obj: the object to pull values from
  :name: the name to use when getting the value
  :fallback: the value to return when has_value(:obj:, :name:) returns False
  """
  present, value = has_value(obj, name)
  if present:
    return value
  else:
    if callable(fallback):
      return fallback()
    else:
      return fallback


def set_value(obj, name, value):
  """A flexible method for setting a value on an object.

  If the object implements __setitem__ (such as a dict) performs obj[name] = value, else performs
  setattr(obj, name, value).

  :obj: the object to set the value on
  :name: the name to assign the value to
  :value: the value to assign
  """
  if hasattr(obj, "__setitem__"):
    obj[name] = value
  else:
    setattr(obj, name, value)


def with_defaults(method, nparams, defaults=None):
  """Call method with nparams positional parameters, all non-specified defaults are passed None.

  :method: the method to call
  :nparams: the number of parameters the function expects
  :defaults: the default values to pass in for the last len(defaults) params
  """
  args = [None] * nparams if not defaults else defaults + max(nparams - len(defaults), 0) * [None]
  return method(*args)


def namedtuple_with_defaults(ntup, defaults=None):
  """Wraps with_defaults for a named tuple.

  :ntup: the namedtuple constructor
  :defaults: the defaultvalues to pass in for the last len(defaults) params
  """
  return with_defaults(ntup, len(ntup._fields), defaults)


def delegate(from_owner, to_owner, methods):
  """Creates methods on from_owner to call through to methods on to_owner.

  :from_owner: the object to delegate to
  :to_owner: the owner on which to delegate from
  :methods: a list of methods to delegate
  """
  for method in methods:
    _delegate(from_owner, to_owner, method)


def _delegate(from_owner, to_owner, method):
  """Creates a method on from_owner to calls through to the same method on to_owner.

  :from_owner: the object to delegate to
  :to_owner: the owner on which to delegate from
  :methods: the method to delegate
  """
  dgate = lambda self, *args, **kwargs: getattr(getattr(self, to_owner), method)(*args, **kwargs)
  dgate.__name__ = method
  dgate.__doc__ = "Delegates to {0}.{1}: {2}".format(to_owner, method, method.__doc__)
  setattr(from_owner, method, dgate)


def flatten_dict(source, ancestors=None):
  """Flattens a dictionary into (key, value) tuples. Where key is a tuple of ancestor keys.

  :source: the root dictionary
  :ancestors: the tuple of ancestors for every key in :source:"""
  if not ancestors:
    ancestors = ()
  for key in source:
    if isinstance(source[key], dict):
      yield from flatten_dict(source[key], ancestors + (key, ))
    else:
      yield (ancestors + (key, ), source[key])


def esc_split(text, delimiter=" ", maxsplit=-1, escape="\\", *, ignore_empty=False):
  """Escape-aware text splitting:

  Split text on on a delimiter, recognizing escaped delimiters."""
  is_escaped = False
  split_count = 0
  yval = []

  for char in text:
    if is_escaped:
      is_escaped = False
      yval.append(char)
    else:
      if char == escape:
        is_escaped = True
      elif char in delimiter and split_count != maxsplit:
        if yval or not ignore_empty:
          yield "".join(yval)
          split_count += 1
        yval = []
      else:
        yval.append(char)

  yield "".join(yval)


def esc_join(iterable, delimiter=" ", escape="\\"):
  """Join an iterable by a delimiter, replacing instances of delimiter in items
  with escape + delimiter.
  """
  rep = escape + delimiter
  return delimiter.join(i.replace(delimiter, rep) for i in iterable)


@contextmanager
def get_file_object(filename, mode="r"):
  """Context manager for a file object. If filename is present, this is the
  same as with open(filename, mode): ...

  If filename is not present, then the file object returned is either
  sys.stdin or sys.stdout depending on the mode.

  :filename: the name of the file, or None for STDIN
  :mode: the mode to open the file with
  """
  if filename is None:
    if mode.startswith("r"):
      yield sys.stdin
    else:
      yield sys.stdout
  else:
    with open(filename, mode) as fobj:
      yield fobj
