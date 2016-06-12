from __future__ import unicode_literals
from namespaces import Namespace

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
