"""A collection of converters, and converter creators

For the purposes of this module, a converter is any function that takes a single value and returns
another value.
"""
from decimal import Decimal
from uuid import UUID, uuid4

from bidon.util import date


def identity(val):
  """Returns the value it is given."""
  return val


def to_int(val):
  """Convert val to an int."""
  if isinstance(val, int):
    return val
  return int(val)


def to_float(val):
  """Convert val to a float."""
  if isinstance(val, float):
    return val
  return float(val)


def to_decimal(val):
  """Convert val to a decimal."""
  if isinstance(val, Decimal):
    return val
  return Decimal(val)


def to_bit(val):
  """Convert val to a bit: either 1 if val evaluates to True, or False otherwise."""
  return 1 if val else 0


def to_bool(val):
  """Convert val to a boolean value."""
  return bool(val)


def to_uuid(val):
  """Convert val to a uuid."""
  if isinstance(val, UUID):
    return val
  return UUID(val)


def to_compressed_string(val, max_length=0):
  """Converts val to a compressed string.

  A compressed string is one with no leading or trailing spaces.

  If val is None, or is blank (all spaces) None is returned.

  If max_length > 0 and  the stripped val is greater than max_length, val[:max_length] is returned.
  """
  if val is None or len(val) == 0:
    return None
  rval = " ".join(val.split())
  if len(rval) == 0:
    return None
  if max_length == 0:
    return rval
  else:
    return rval[:max_length]


def to_now(_):
  """Returns the current timestamp, with a utc timezone."""
  return date.utc_now()


def to_none(_):
  """Returns None."""
  return None


def to_true(_):
  """Returns True."""
  return True


def to_false(_):
  """Returns False."""
  return False


def to_empty_string(_):
  """Returns the empty string."""
  return ""


def to_new_uuid(_):
  """Returns a new randomly generated UUID."""
  return uuid4()


def to_date(val, fmt=None):
  return date.parse_date(val, fmt)


def to_time(val, fmt=None):
  return date.parse_time(val, fmt)


def to_datetime(val, fmt=None):
  return date.parse_datetime(val, fmt)


def to_formatted_datetime(fmt):
  """Returns a datetime converter using fmt."""
  return lambda val: to_datetime(val, fmt)


def incrementor(start=0, step=1):
  """Returns a function that first returns the start value, and returns previous value + step on
  each subsequent call.
  """
  def fxn(_):
    """Returns the next value in the sequnce defined by [start::step)"""
    nonlocal start
    rval = start
    start += step
    return rval
  return fxn


def string_trimmer(max_length=0):
  """The same as partial(to_compressed_string(max_length=max_length))"""
  return lambda val: to_compressed_string(val, max_length)


def static_value(val):
  """Returns a function that always returns val."""
  return lambda _: val


def rounded_decimal(places):
  """Returns a lambda that converts its value to a decimal and then rounds the value by places."""
  return lambda val: round(to_decimal(val), places)


def index_resolver(index, strict=False):
  """Returns a function that accepts a value and returns index[value]."""
  if strict:
    return lambda id_: index[id_]
  else:
    return index.get


def accept_none_wrapper(fxn):
  """Wraps a function, returning None if None is passed in, and otherwise passing the
  value along to the given function.
  """
  def wrapper(val):
    """If val is None, return None, otherwise pass the value along to fxn."""
    if val is None:
      return None
    else:
      return fxn(val)
  return wrapper


def try_wrapper(fxn):
  """Wraps a function, returning (True, fxn(val)) if successful, (False, val) if not."""
  def wrapper(val):
    """Try to call fxn with the given value. If successful, return (True, fxn(val)), otherwise
    returns (False, val).
    """
    try:
      return (True, fxn(val))
    except Exception:
      return (False, val)
  return wrapper
