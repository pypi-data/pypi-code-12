from .algorithms import *

class Complex(object):

    def __init__(self, impl):
        assert impl is not None
        self._impl = impl

    @property
    def capd(self):
        return self._impl

    @property
    def dim(self):
        return self._impl.dim()

    @property
    def cardinality(self):
        return self._impl.cardinality()

    def betti(self):
        return BettiNumbersOverZ(self)()
