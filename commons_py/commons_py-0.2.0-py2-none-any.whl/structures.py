#!/usr/bin/python
# -*- coding: utf-8 -*-

import math

FLOAT_PRECISION = 14
""" The amount of precision (in decimal places) that
is going to be used for the decimal internal usage """

class Decimal(float):
    """
    Fixed point rational number representation/manipulation
    structure aimed at replacing the internal python data
    structure with the same name.

    Provides a simple unified way of re-using the float data
    type to performed fixed point operations, using techniques
    around the special rounding method.

    The implementation of the data structure is not aimed at
    performance and because of that it should not be used for
    task that are considered performance intensive.
    """

    def __new__(self, value = 0.0):
        value = float(value)
        integer = abs(int(value // 1))
        count = 1 if integer == 0 else int(math.log10(integer)) + 1
        places = FLOAT_PRECISION - count
        self.places = places
        value = round(value, places)
        return super(Decimal, self).__new__(self, value)

    def __hash__(self):
        return float.__hash__(self)

    def __cmp__(self, other):
        other = self._normalize(other)
        if float.__gt__(self, other): return 1
        if float.__lt__(self, other): return -1
        return 0

    def __lt__(self, other):
        other = self._normalize(other)
        return float.__lt__(self, other)

    def __le__(self, other):
        other = self._normalize(other)
        return float.__le__(self, other)

    def __eq__(self, other):
        other = self._normalize(other)
        return float.__eq__(self, other)

    def __ne__(self, other):
        other = self._normalize(other)
        return float.__ne__(self, other)

    def __gt__(self, other):
        other = self._normalize(other)
        return float.__gt__(self, other)

    def __ge__(self, other):
        other = self._normalize(other)
        return float.__ge__(self, other)

    def __add__(self, other):
        result = float.__add__(self, other)
        return Decimal(result)

    def __radd__(self, other):
        result = float.__radd__(self, other)
        return Decimal(result)

    def __sub__(self, other):
        result = float.__sub__(self, other)
        return Decimal(result)

    def __rsub__(self, other):
        result = float.__rsub__(self, other)
        return Decimal(result)

    def __mul__(self, other):
        result = float.__mul__(self, other)
        return Decimal(result)

    def __rmul__(self, other):
        result = float.__rmul__(self, other)
        return Decimal(result)

    def __floordiv__(self, other):
        result = float.__floordiv__(self, other)
        return Decimal(result)

    def __rfloordiv__(self, other):
        result = float.__rfloordiv__(self, other)
        return Decimal(result)

    def __div__(self, other):
        result = float.__div__(self, other)
        return Decimal(result)

    def __rdiv__(self, other):
        result = float.__rdiv__(self, other)
        return Decimal(result)

    def __truediv__(self, other):
        result = float.__truediv__(self, other)
        return Decimal(result)

    def __rtruediv__(self, other):
        result = float.__rtruediv__(self, other)
        return Decimal(result)

    def __mod__(self, other):
        result = float.__mod__(self, other)
        return Decimal(result)

    def __rmod__(self, other):
        result = float.__rmod__(self, other)
        return Decimal(result)

    def __and__(self, other):
        other = self._normalize(other)
        return float.__and__(self, other)

    def __rand__(self, other):
        other = self._normalize(other)
        return float.__rand__(self, other)

    def __or__(self, other):
        other = self._normalize(other)
        return float.__or__(self, other)

    def __ror__(self, other):
        other = self._normalize(other)
        return float.__ror__(self, other)

    def __xor__(self, other):
        other = self._normalize(other)
        return float.__xor__(self, other)

    def __rxor__(self, other):
        other = self._normalize(other)
        return float.__rxor__(self, other)

    def __pos__(self):
        result = float.__pos__(self)
        return Decimal(result)

    def __neg__(self):
        result = float.__neg__(self)
        return Decimal(result)

    def __abs__(self):
        result = float.__abs__(self)
        return Decimal(result)

    def __invert__(self):
        result = float.__invert__(self)
        return Decimal(result)

    def __round__(self, n):
        result = float.__round__(self, n)
        return Decimal(result)

    def __floor__(self):
        result = math.floor(float(self))
        return Decimal(result)

    def __ceil__(self):
        result = math.ceil(float(self))
        return Decimal(result)

    def __trunc__(self):
        result = float.__trunc__(self)
        return Decimal(result)

    def _normalize(self, value):
        if not type(value) == float: return value
        return round(value, self.places)
