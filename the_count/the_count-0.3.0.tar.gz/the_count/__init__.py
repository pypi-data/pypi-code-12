
class TheCount(object):
  def __init__(self, sums = None):
    self.sums = sums or {}

  def tally(self, thing, count = 1):
    self.sums[thing] = self.sums.get(thing, 0) + count

  def keys(self):
    return self.sums.keys()

  def __getitem__(self, key):
    return self.sums[key]

  def get(self, key, d = 0):
    return self.sums.get(key, d)

  def total(self, *keys):
    """
    Returns the number of times the key has occurred, or 0
    if the key was never encountered.
    """
    return sum((self.get(k) for k in keys))

  def grand_total(self):
    """
    Returns the total number of things that were tallied.
    AKA: It's the sum of everything.
    """
    return sum(self.itervalues())

  def consolidate(self, mapping):
    """
    Returns a new TheCount instance that consolidates many
    terms into a single entry.  This is useful for summarizing
    datasets.
    """
    sums = {}
    for k, terms in mapping.iteritems():
      sums[k] = self.total(*terms)
    return TheCount(sums)

  def select(self, func):
    """
    Create a new TheCount instance that only retains that
    key/value pairs such that func(key, value) == True
    """
    new_sum = {}
    for k, v in self.iteritems():
      if func(k, v):
        new_sum[k] = v
    return TheCount(new_sum)

  def reject(self, func):
    """
    Create a new TheCount instance that only retains that
    key/value pairs such that func(key, value) == False
    """
    new_sum = {}
    for k, v in self.iteritems():
      if not func(k, v):
        new_sum[k] = v
    return TheCount(new_sum)


  def iteritems(self):
    return self.sums.iteritems()

  def iterkeys(self):
    return self.sums.iterkeys()

  def itervalues(self):
    return self.sums.itervalues()

  def __iter__(self):
    return iter(self.sums)

  def __list__(self):
    return list(self.sums)

  def clear(self):
    return self.sums.clear()

  def __len__(self):
    return len(self.sums)

  def __add__(self, counter):
    keys = set(self.keys() + counter.keys())
    sums = {}
    for k in keys:
      sums[k] = self.total(k) + counter.total(k)

    return TheCount(sums)

  def __str__(self):
    return str(self.sums)

  __repr__ = __str__


