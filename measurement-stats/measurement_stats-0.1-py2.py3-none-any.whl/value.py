from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import math
import random

if sys.version > '3':
    long = int


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
    shifted = round(value*magnitude)
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


class ValueUncertainty(object):
    """

    """

    def __init__(self, value =0.0, uncertainty =1.0, **kwargs):
        self.raw = float(value)
        self.raw_uncertainty = abs(float(uncertainty))

    @property
    def value(self):
        uncertainty = self.uncertainty
        order = least_significant_order(uncertainty)
        return round_to_order(self.raw, order)

    @value.setter
    def value(self, value):
        self.raw = float(value)

    @property
    def uncertainty(self):
        return round_significant(abs(self.raw_uncertainty), 1)

    @uncertainty.setter
    def uncertainty(self, value):
        self.raw_uncertainty = float(value)

    @property
    def html_label(self):
        return '%.15g &#177; %s' % (self.value, self.uncertainty)

    @property
    def label(self):
        return '%.15g +/- %s' % (self.value, self.uncertainty)

    @property
    def raw_label(self):
        return '%.15g +/- %.15g' % (
            round_significant(self.raw, 6),
            self.uncertainty
        )

    def from_dict(self, source):
        self.raw = source['raw']
        self.raw_uncertainty = source['raw_uncertainty']

    def to_dict(self):
        return dict(
            raw=self.raw,
            raw_uncertainty=self.raw_uncertainty
        )

    def serialize(self):
        return dict(
            value=self.value,
            uncertainty=self.uncertainty,
            raw=self.raw,
            raw_uncertainty=self.raw_uncertainty
        )

    def clone(self):
        """clone doc..."""
        return ValueUncertainty(
            value=self.raw,
            uncertainty=self.raw_uncertainty
        )

    def update(self, value = None, uncertainty = None):

        if value is not None:
            self.raw = value

        if uncertainty is not None:
            self.raw_uncertainty = uncertainty

    def freeze(self):
        """

        :return:
        :rtype: ValueUncertainty
        """
        self.raw = self.value
        self.raw_uncertainty = self.uncertainty
        return self

    @classmethod
    def create_random(
            cls, min_value =-1.0, max_value =1.0,
            min_uncertainty =0.1, max_uncertainty =2.0):
        """

        :param min_value:
        :param max_value:
        :param min_uncertainty:
        :param max_uncertainty:
        :return:
        """

        return ValueUncertainty(
            value=random.uniform(min_value, max_value),
            uncertainty=random.uniform(min_uncertainty, max_uncertainty) )

    def __pow__(self, power, modulo=None):
        if equivalent(self.raw, 0.0, 1e-5):
            return self.__class__(self.raw, self.raw_uncertainty)

        val = self.raw ** power
        unc = abs(val * float(power) * self.raw_uncertainty / self.raw)
        return self.__class__(val, unc)

    def __add__(self, other):
        try:
            val = self.raw + other.raw
            unc = math.sqrt(
                self.raw_uncertainty ** 2 +
                other.raw_uncertainty ** 2
            )
        except Exception:
            val = float(other) + self.raw
            unc = self.raw_uncertainty

        return self.__class__(val, unc)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        try:
            val = self.raw - other.raw
            unc = math.sqrt(
                self.raw_uncertainty ** 2 +
                other.raw_uncertainty ** 2
            )
        except Exception:
            val = self.raw - float(other)
            unc = self.raw_uncertainty

        return self.__class__(val, unc)

    def __rsub__(self, other):
        try:
            val = other.raw - self.raw
            unc = math.sqrt(
                self.raw_uncertainty ** 2 +
                other.raw_uncertainty ** 2
            )
        except Exception:
            val = float(other) - self.raw
            unc = self.raw_uncertainty

        return self.__class__(val, unc)

    def __mul__(self, other):
        try:
            val = self.raw * other.raw
            unc = abs(val)*math.sqrt(
                (self.raw_uncertainty / self.raw) ** 2 +
                (other.raw_uncertainty / other.raw) ** 2)
        except ZeroDivisionError:
            val = 0.0
            unc = math.sqrt(
                self.raw_uncertainty ** 2 +
                other.raw_uncertainty ** 2
            )
        except Exception:
            val = float(other) * self.raw
            unc = abs(float(other) * self.raw_uncertainty)

        return self.__class__(val, unc)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        try:
            val = self.raw/other.raw
            unc = abs(val) * math.sqrt(
                (self.raw_uncertainty / self.raw) ** 2 +
                (other.raw_uncertainty / other.raw) ** 2)
        except ZeroDivisionError:
            if equivalent(self.raw, 0.0, 1e-6):
                val = 0.0
                unc = math.sqrt(
                    self.raw_uncertainty ** 2 +
                    other.raw_uncertainty ** 2
                )
            else:
                raise
        except Exception:
            val = self.raw / float(other)
            unc = abs(self.raw_uncertainty / float(other))

        return self.__class__(val, unc)

    def __rtruediv__(self, other):
        return self.__truediv__(other)

    def __div__(self, other):
        return self.__truediv__(other)

    def __rdiv__(self, other):
        return self.__rtruediv__(other)

    def __repr__(self):
        return self.__str__()

    def __unicode__(self):
        """__unicode__ doc..."""
        return '<%s %s>' % (self.__class__.__name__, self.label)

    def __str__(self):
        return '<%s %s>' % (self.__class__.__name__, self.label)

