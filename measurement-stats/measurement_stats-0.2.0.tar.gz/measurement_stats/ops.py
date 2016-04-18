from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys

if sys.version > '3':
    long = int


def sqrt_sum_of_squares(*args):
    """
    Computes the square-root of the sum of the squares for the combined list
    of numbers in the args list

    :param args:
    :return:
    """

    out = 0.0
    for arg in args:
        out += float(arg) * float(arg)

    return out ** 0.5


def is_number(value):
    """
    Determines whether or not the specified value is a numeric type, either
    integer or float.

    :param value:
    :return:
    """

    return isinstance(value, (int, long, float))


def linear_space(min_value=0, max_value=1.0, length=10, round_op=None):
    """
    Returns a list of linear-spaced values with min_value and max_value as
    the boundaries with the specified number (length) of entries. If
    roundToIntegers is True, each value will be rounded to the nearest
    integer.

    :param min_value:
    :param max_value:
    :param length:
    :param round_op:
    :return:
    """

    out = []
    value = min_value
    length = max(2, length)
    delta = (float(max_value) - float(min_value)) / float(length - 1.0)

    for index in range(length - 1):
        out.append(round_op(value) if round_op else value)
        value += delta

    out.append(round_op(max_value) if round_op else max_value)
    return out




