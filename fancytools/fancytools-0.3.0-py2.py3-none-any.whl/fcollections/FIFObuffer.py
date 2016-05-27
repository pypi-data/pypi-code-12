# -*- coding: utf-8 -*-
import numpy as np


class FIFObuffer(object):
    """
    A circular FIFO buffer implemented on top of numpy.

    >>> a = FIFObuffer(shape=3)
    >>> a.add(2)
    >>> a.add(33)
    >>> a.add(124)
    >>> print a
    [   2.   33.  124.]
    >>> a.add(21)
    >>> a.add(2456)
    >>> print a
    [  124.    21.  2456.]
    """

    def __init__(self, shape, dtype=np.float32, filled=False):
        self._cache = np.zeros(shape, dtype)
        self._values = np.zeros(shape, dtype)
        if not isinstance(shape,int):
            raise Exception('%s can only handle 1darrays at the moment, shape has to be int' %self.__class__.__name__)
        self.shape = shape
        self.size = shape
        self._splitPos = 0
        if filled:
            self._ind = self.shape
        else:
            self._ind = 0
        self._cached = False
        self._splitValue = 1


    def setNextLineEveryNValues(self, n):
        self._splitValue = 1/float(n)
        if int(self._splitValue) == self._splitValue:
            self._splitValue = int(self._splitValue)


    def add(self, value):
        """
        Add a value to the buffer.
        """
        ind = int(self._ind % self.shape)
        self._pos = self._ind % self.shape
        self._values[ind] = value
        if self._ind < self.shape:
            self._ind += 1 #fast fill
        else:
            self._ind += self._splitValue
            self._splitPos += self._splitValue
        self._cached = False


    def array(self):
        """
        Returns a numpy array containing the last stored values.
        """
        if self._ind < self.shape:
            return self._values[:self._ind]
        if not self._cached:
            ind = int(self._ind % self.shape)
            self._cache[:self.shape - ind] = self._values[ind:]
            self._cache[self.shape - ind:] = self._values[:ind]
            self._cached = True
        return self._cache


    def __len__(self):
        return min(int(self._ind), self.shape)


    @property
    def position(self):
        return self.__len__()-1


    def splitPos(self):
        '''return the position of where to split the array 
        to get the values in the right order'''
        if self._ind < self.shape:
            return 0
        v = int(self._splitPos)
        if v >= 1:
            self._splitPos = 0
        return v


    def __repr__(self):
        return str(self.array())


    def __getitem__(self, key):
        return self.array()[key]



if __name__ == "__main__":
    import doctest
    doctest.testmod()
