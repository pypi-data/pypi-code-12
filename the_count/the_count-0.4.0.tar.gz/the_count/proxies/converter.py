
from .core import Proxy

class Converter(Proxy):
  def __init__(self, child, converter):
    self._child = child
    self.converter = converter

  def replicate(self, child):
    return Converter(child, self.converter)

  def tally(self, key, *args):
    return self._child.tally(self.converter(key), *args)

  def __getitem__(self, key):
    return self._child[self.converter(key)]

  def get(self, key, *args):
    return self._child.get(self.converter(key), *args)

  def consolidate(self, mapping):
    new_mapping = {}
    for k, terms in mapping.iteritems():
      new_mapping[self.converter(k)] = (self.converter(t) for t in terms)
    return self.replicate(self._child.consolidate(new_mapping))
