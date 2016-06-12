from __future__ import unicode_literals
import keyword
import re

def isidentifier(string):
  '''Backport of python3's str#isidentifier.
  Checks that the string begins with an alphabetic character or underscore and
  contains only alphanumeric characters and underscores.
  '''
  return bool(re.match(r'^[^\d\W]\w*$', string))

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
    return FrozenNamespace(self)

class FrozenNamespace(Namespace):
  '''Immutable, hashable Namespace.'''

  __hash_key = '__hash'

  def __init__(self, *args, **kwargs):
    self.__dict__[FrozenNamespace.__hash_key] = None
    super(self.__class__, self).__init__(*args, **kwargs)

  def __setattr__(self, name, value):
    '''Overridden with an exception to preserve immutability.
    Behaves similarly to collections.namedtuple#__setattr__.'''
    raise AttributeError(
      "'{}' object has no attribute '__setattr__'".format(type(self).__name__)
    )

  def __hash__(self):
    '''Caches lazily-evaluated hash for performance.'''
    if self.__dict__[FrozenNamespace.__hash_key] is None:
      self.__dict__[FrozenNamespace.__hash_key] = hash(frozenset(self.items()))
    return self.__dict__[FrozenNamespace.__hash_key]

  def mutable(self):
    return Namespace(self)
