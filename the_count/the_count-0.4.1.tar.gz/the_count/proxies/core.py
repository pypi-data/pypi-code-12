
class Proxy(object):
  def __init__(self, child):
    self._child = child

  def replicate(self, child):
    raise NotImplementedError()

  def __getattr__(self, name):
    return getattr(self._child, name)

  def consolidate(self, mapping):
    return self.replicate(self._child.consolidate(mapping))

  def select(self, func):
    return self.replicate(self._child.select(func))

  def reject(self, func):
    return self.replicate(self._child.reject(func))

  def __add__(self, counter):
    return self.replicate(self._child + counter)

  def __iter__(self):
    return iter(self._child)

  def __len__(self):
    return len(self._child)

  def __str__(self):
    return str(self._child)

  __repr__ = __str__
