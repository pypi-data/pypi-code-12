from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import random
import math

from measurement_stats.value import  value_ops


class ValueUncertainty(object):
    """
    A data type representation of a measurement value and its corresponding
    uncertainty. This type overrides the common mathematical operators, which
    enables transparent propagation of uncertainties.

    Each instance stores the raw value and raw uncertainties as they were
    assigned. However, the value and uncertainty attributes are properly
    rounded according the single significant uncertainty digit rules for
    displaying values with uncertainties.

    The raw values should be used for intermediate calculations to minimize
    excessive rounding errors during computation, but not used when presenting
    final values.
    """

    def __init__(self, value=0.0, uncertainty=1.0, **kwargs):
        self.raw = float(value)
        self.raw_uncertainty = abs(float(uncertainty))

    @property
    def value(self):
        """
        :return:
            Returns the numerical value, which has been rounded according to
            the corresponding uncertainty
        """

        uncertainty = self.uncertainty
        order = value_ops.least_significant_order(uncertainty)
        return value_ops.round_to_order(self.raw, order)

    @value.setter
    def value(self, value):
        self.raw = float(value)

    @property
    def uncertainty(self):
        """
        :return:
            Returns the uncertainty value, which has been rounded to a single
            significant digit for properly citing of the measurement
        """
        return value_ops.round_significant(abs(self.raw_uncertainty), 1)

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
            value_ops.round_significant(self.raw, 6),
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

    def update(self, value=None, uncertainty=None):

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
            cls, min_value=-1.0, max_value=1.0,
            min_uncertainty=0.1, max_uncertainty=2.0):
        """

        :param min_value:
        :param max_value:
        :param min_uncertainty:
        :param max_uncertainty:
        :return:
        """

        return ValueUncertainty(
            value=random.uniform(min_value, max_value),
            uncertainty=random.uniform(min_uncertainty, max_uncertainty))

    def __pow__(self, power, modulo=None):
        if value_ops.equivalent(self.raw, 0.0, 1e-5):
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
            unc = abs(val) * math.sqrt(
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
            val = self.raw / other.raw
            unc = abs(val) * math.sqrt(
                (self.raw_uncertainty / self.raw) ** 2 +
                (other.raw_uncertainty / other.raw) ** 2)
        except ZeroDivisionError:
            if value_ops.equivalent(self.raw, 0.0, 1e-6):
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
