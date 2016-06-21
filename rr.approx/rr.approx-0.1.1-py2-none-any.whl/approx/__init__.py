"""
This module exposes the Approx class which allows approximate comparison of floating point
values. Two values are considered equal if their relative difference is smaller than a given
relative tolerance (http://en.wikipedia.org/wiki/Relative_difference). The base comparison is:

    |x-y| / max(|x|,|y|) < rtol

This formula breaks down when one of the numbers is 0, since no number other than 0 itself is
considered approximately == 0 unless rtol > 1. Replacing x by 0 in the formula and assuming
y != 0, yields

    |y| / |y| < rtol

So rtol would effectively have to be > 1 for the formula to accept any non-zero number as "close
enough" to 0. Note however that rtol should normally be a small positive number (e.g. 1e-6), so
this is not satisfactory.

To fix this, we introduce a second tolerance parameter: absolute tolerance. First, we transform the
previous inequality by multiplying both sides by max(|x|,|y|). Since this is > 0 (because at least
one of the numbers is != 0), the direction of the inequality is maintained, leading to

    |x-y| < rtol * max(|x|,|y|)

Now, we simply add the absolute tolerance to the right-hand side of the inequality

    |x-y| < atol + rtol * max(|x|,|y|)

This keeps at least the absolute tolerance for when one of the numbers is 0. Additionally, the
influence of absolute tolerance should fade when comparing large numbers, since the other term
should be much larger.
"""
from __future__ import absolute_import
from itertools import izip_longest
from collections import Iterable
import pkgutil


# Module-level variables
__version__ = pkgutil.get_data(__name__, "VERSION").strip()
_rtol = 1e-9  # default relative tolerance
_atol = 1e-12  # default absolute tolerance


def tolerance(x, y):
    """Compute the final tolerance for the approximate comparison of x and y."""
    global _atol, _rtol
    x = float(x)
    y = float(y)
    return _atol + _rtol * max(abs(x), abs(y))


def equal(x, y):
    """
    Approximate floating point comparison using absolute and relative epsilons. This function is
    equivalent to

        |x - y| <= atol + rtol * max(|x|, |y|)

    This is very similar to what is done in numpy, but this function is symmetric, that is,
    the order of the two numbers is irrelevant to the result. In numpy.isclose(), the relative
    tolerance is multiplied by the absolute value of the second number, so calling the function
    with reversed arguments can give different results, which makes no sense at all. They're even
    aware of that, there's a note on their website, but they don't fix it for some reason...
    """
    x = float(x)
    y = float(y)
    if x == y:
        return True
    global _atol, _rtol
    z = abs(x - y) - _atol
    return z <= 0.0 or z <= _rtol * max(abs(x), abs(y))


class Approx(float):
    """
    A float subclass to mitigate (but does not eliminate!) floating point rounding errors by
    comparing approximately. Comparison operators are redefined to use the absolute and relative
    tolerances defined in this module.
    """
    __slots__ = ()  # prevent creation of a dictionary per Approx instance

    def __repr__(self):
        return float.__repr__(self) + "~"

    def __str__(self):
        return float.__str__(self) + "~"

    tolerance = tolerance
    # --------------------------------------------------------------------------
    # Rich comparison operators
    __eq__ = equal

    def __ne__(self, x):
        return not self.__eq__(x)

    def __le__(self, x):
        return float(self) <= float(x) or self.__eq__(x)

    def __lt__(self, x):
        return float(self) < float(x) and not self.__eq__(x)

    def __ge__(self, x):
        return float(self) >= float(x) or self.__eq__(x)

    def __gt__(self, x):
        return float(self) > float(x) and not self.__eq__(x)

    # --------------------------------------------------------------------------
    # Arithmetic operators
    def __neg__(self):
        return type(self)(-float(self))

    def __pos__(self):
        return type(self)(+float(self))

    def __abs__(self):
        return type(self)(abs(float(self)))

    def __add__(self, other):
        return type(self)(float(self) + other)

    def __sub__(self, other):
        return type(self)(float(self) - other)

    def __mul__(self, other):
        return type(self)(float(self) * other)

    def __div__(self, other):
        return type(self)(float(self) / other)

    __truediv__ = __div__

    def __floordiv__(self, other):
        return type(self)(float(self) // other)

    def __mod__(self, other):
        return type(self)(float(self) % other)

    def __pow__(self, other, modulo=None):
        return type(self)(pow(float(self), other, modulo))

    __radd__ = __add__

    def __rsub__(self, other):
        return type(self)(other - float(self))

    __rmul__ = __mul__

    def __rdiv__(self, other):
        return type(self)(other / float(self))

    __rtruediv__ = __rdiv__

    def __rfloordiv__(self, other):
        return type(self)(other // float(self))

    def __rmod__(self, other):
        return type(self)(other % float(self))

    def __rpow__(self, other):
        return type(self)(other ** float(self))

    # --------------------------------------------------------------------------
    # Rich comparison operators for iterables
    @classmethod
    def _apply(cls, op, x, y):
        """This internal function allows the application of rich comparison operators between two
        numbers, a number and a (possibly nested) sequence of numbers, or two (flat/nested)
        sequences of numbers. When comparing two sequences, missing values are filled with NaN.
        Returns a generator expression in case sequences are involved, or a plain old boolean if
        two numbers are being compared.
        """
        x_is_iterable = isinstance(x, Iterable)
        y_is_iterable = isinstance(y, Iterable)
        if x_is_iterable and y_is_iterable:
            return (cls._apply(op, u, v) for u, v in izip_longest(x, y, fillvalue=float("NaN")))
        elif x_is_iterable:
            return (cls._apply(op, u, y) for u in x)
        elif y_is_iterable:
            return (cls._apply(op, x, v) for v in y)
        else:
            return op(cls(x), y)

    @classmethod
    def eq(cls, x, y):
        return cls._apply(x, y, cls.__eq__)

    @classmethod
    def ne(cls, x, y):
        return cls._apply(x, y, cls.__ne__)

    @classmethod
    def le(cls, x, y):
        return cls._apply(x, y, cls.__le__)

    @classmethod
    def lt(cls, x, y):
        return cls._apply(x, y, cls.__lt__)

    @classmethod
    def ge(cls, x, y):
        return cls._apply(x, y, cls.__ge__)

    @classmethod
    def gt(cls, x, y):
        return cls._apply(x, y, cls.__gt__)


class ApproxContext(object):
    """
    A context manager which temporarily changes the relative and/or absolute tolerances for
    numeric comparisons. Note that this context manager *can* be reused multiple times.
    """
    def __init__(self, rtol=None, atol=None):
        global _rtol, _atol
        self.rtol = rtol if rtol is not None else _rtol
        self.atol = atol if atol is not None else _atol
        self.orig_rtol = None
        self.orig_atol = None

    def __repr__(self):
        return "{}(rtol={}, atol={})".format(type(self).__name__, self.rtol, self.atol)

    @property
    def active(self):
        """A context is active if it has been applied (and it cannot be applied multiple times)."""
        return self.orig_rtol is not None

    def apply(self):
        """Set the current relative and/or absolute tolerance for approximate comparisons."""
        if self.active:
            raise ValueError("{} is already active".format(self))
        global _rtol, _atol
        self.orig_rtol = _rtol
        self.orig_atol = _atol
        _rtol = self.rtol
        _atol = self.atol

    def restore(self):
        """Restore the values of 'rtol' and 'atol' that were saved when the context was applied."""
        if not self.active:
            raise ValueError("{} is not active".format(self))
        global _rtol, _atol
        _rtol = self.orig_rtol
        _atol = self.orig_atol
        self.orig_rtol = None
        self.orig_atol = None

    def __enter__(self):
        self.apply()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.restore()


# Provide the context class as an alias through Approx
Approx.Context = ApproxContext
