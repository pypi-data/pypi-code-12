from __future__ import unicode_literals
import keyword
from namespaces import isidentifier

class Namespace(dict):
  '''A dictionary with attributes instead of keys.
  The Namespace API is inspired by collections.namedtuple.
  Attributes provided as strings must be valid python identifiers.
  Access via __getitem__ and __setitem__ (ie. `namespace[key]`) is disabled.
  '''

  def __init__(self, *args, **kwargs):
    d = dict(*args, **kwargs)
    for k in d:
      if not isinstance(k, str) and not isinstance(k, unicode):
        raise TypeError(
          "Field names must be {} or {}, not {}: {}".format(
            str, unicode, type(k), repr(k)
          )
        )
      if not isidentifier(k):
        raise ValueError("Field name is not a valid identifier: {}".format(repr(k)))
      if keyword.iskeyword(k):
        raise ValueError("Field name cannot be a python keyword: {}".format(repr(k)))
    dict.__init__(self, d)

  def __getitem__(self, name):
    raise AttributeError(
      "'{}' object has no attribute '__getitem__'".format(type(self).__name__)
    )

  def __setitem__(self, name, value):
    raise AttributeError(
      "'{}' object has no attribute '__setitem__'".format(type(self).__name__)
    )

  def __getattr__(self, name):
    '''Behaves similarly to collections.namedtuple#__getattr__.'''
    try:
      return dict.__getitem__(self, name)
    except KeyError:
      raise AttributeError(
        "'{}' object has no attribute '{}'".format(type(self).__name__, name)
      )

  def __setattr__(self, name, value):
    dict.__setitem__(self, name, value)

  def __repr__(self):
    '''Representation is a valid python expression for creating a Namespace
    (assuming contents also implement __repr__ as valid python expressions).'''
    kwargs_strs = ['{}={}'.format(k,repr(v)) for k,v in self.iteritems()]
    return '{}({})'.format(type(self).__name__, ', '.join(kwargs_strs))

  def __eq__(self, other):
    return isinstance(other, type(self)) and dict.__eq__(self, other)

  def __ne__(self, other):
    return not self == other

  def immutable(self):
    from namespaces import FrozenNamespace
    return FrozenNamespace(self)
