"""
"""

from fractions import Fraction

# versioneer stuff
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

BOOLEAN_TRUE = {'1', 'yes', 'true', 'on', }
BOOLEAN_FALSE = {'0', 'no', 'false', 'off', }


def str_to_float_converter():
    def str_to_float(s):
        """
        Convert a string to a float
        """
        return float(Fraction(s))
    return str_to_float


def str_to_int_converter():
    def str_to_int(s):
        """
        Convert a string to a int
        """
        frac = Fraction(s)
        if frac.denominator == 1:
            return int(frac)
        raise ValueError("{} is not an integer".format(frac))
    return str_to_int


def str_to_bool_converter(
    boolean_true=None, boolean_false=None, additional=True
):
    if boolean_true is None:
        boolean_true = set()
    if boolean_false is None:
        boolean_false = set()
    if additional:
        boolean_true.update(BOOLEAN_TRUE)
        boolean_false.update(BOOLEAN_FALSE)
    if not boolean_true.isdisjoint(boolean_false):
        raise ValueError(
            "{} are both True and False".format(boolean_true & boolean_false)
        )

    def str_to_bool(s):
        s = s.strip().lower()
        if s in boolean_true:
            return True
        elif s in boolean_false:
            return False
        raise ValueError("{} is neither True nor False.".format(s))
    return str_to_bool
