from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import math
import random

if sys.version > '3':
    long = int


__all__ = [
    'order_of_magnitude',
    'round_significant',
    'least_significant_order',
    'equivalent',
    'round_to_order'
]


def order_of_magnitude(value):
    """
    Returns the order of magnitude of the most significant digit of the
    specified number. A value of zero signifies the ones digit, as would be
    the case in [Number]*10^[Order].

    :param value:
    :return:
    """

    x = abs(float(value))
    offset = 0 if x >= 1.0 else -1
    return int(math.log10(x) + offset)


def round_significant(value, digits):
    """

    :param value:
    :param digits:
    :return:
    """

    if value == 0.0:
        return 0

    value = float(value)
    d = math.ceil(math.log10(-value if value < 0  else value))
    power = digits - int(d)

    magnitude = math.pow(10, power)
    shifted = round(value * magnitude)
    return shifted / magnitude


def least_significant_order(value):
    """

    :param value:
    :return:
    """

    om = 0

    if isinstance(value, (int, long)) or long(value) == value:
        value = long(value)

        while om < 10000:
            om += 1
            magnitude = math.pow(10, -om)
            test = float(value) * magnitude
            if long(test) != test:
                return om - 1
        return 0

    while om < 10000:
        om -= 1
        magnitude = math.pow(10, -om)
        test = value * magnitude
        if equivalent(test, int(test)):
            return om
    return 0


def equivalent(a, b, epsilon=None, machine_epsilon_factor=100.0):
    """

    :param a:
    :param b:
    :param epsilon:
    :param machine_epsilon_factor:
    :return:
    """

    if epsilon is None:
        epsilon = machine_epsilon_factor * sys.float_info.epsilon
    return abs(float(a) - float(b)) < epsilon


def round_to_order(value, order, round_op=None, as_int=False):
    """

    :param value:
    :param order:
    :param round_op:
    :param as_int:
    :return:
    """

    if round_op is None:
        round_op = round

    if order == 0:
        value = round(float(value))
        return int(value) if as_int else value

    scale = math.pow(10, order)
    value = scale * round_op(float(value) / scale)
    return int(value) if as_int else value





