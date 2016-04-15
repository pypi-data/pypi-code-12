from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math

from measurement_stats import value


class Angle(object):
    """A type for representing angular measurements with uncertainties"""

    def __init__(self, **kwargs):
        self._angle = 0.0
        self._unc = 1.0

        if 'uncertainty' in kwargs:
            self.uncertainty = kwargs.get('uncertainty')
        elif 'uncertainty_degrees' in kwargs:
            self.uncertainty_degrees = kwargs.get('uncertainty_degrees')

        if 'degrees' in kwargs:
            self.degrees = kwargs.get('degrees')
        elif 'radians' in kwargs:
            self.radians = kwargs.get('radians')

    @property
    def value(self):
        return value.ValueUncertainty(self.radians, self.uncertainty)

    @property
    def value_degrees(self):
        return value.ValueUncertainty(self.degrees, self.uncertainty_degrees)

    @property
    def uncertainty(self):
        return self._unc

    @uncertainty.setter
    def uncertainty(self, v):
        self._unc = v

    @property
    def uncertainty_degrees(self):
        return math.degrees(self._unc)

    @uncertainty_degrees.setter
    def uncertainty_degrees(self, v):
        self._unc = math.radians(v)

    @property
    def radians(self):
        return self._angle

    @radians.setter
    def radians(self, v):
        self._angle = float(v)

    @property
    def degrees(self):
        return math.degrees(self._angle)

    @degrees.setter
    def degrees(self, v):
        self._angle = math.radians(float(v))

    @property
    def pretty_print(self):
        return value.round_significant(self.degrees, 3)

    def clone(self):
        """clone doc..."""
        return self.__class__(radians=self._angle, uncertainty=self._unc)

    def constrain_to_revolution(self):
        """
        Constrains the angle to within the bounds [0, 360] by removing
        revolutions.
        """

        radians = self.radians
        while radians < 0:
            radians += 2.0*math.pi
        degrees = math.degrees(radians) % 360.0
        self.radians = math.radians(degrees)
        return self

    def difference_between(self, angle):
        """
        Returns a new Angle instance that is the smallest difference between
        this angle the one specified in the arguments.

        :param angle:
        :return:
        :rtype: Angle
        """

        a = self.clone().constrain_to_revolution()
        b = angle.clone().constrain_to_revolution()

        result = a - b
        return Angle(
            degrees=((result.degrees + 180.0) % 360.0) - 180.0,
            uncertainty=result.uncertainty
        )

    def __pow__(self, power, modulo=None):
        v = self.value ** power
        return self.__class__(
            radians=v.raw,
            uncertainty=v.raw_uncertainty
        )

    def __add__(self, other):
        v = self.value + other.value
        return self.__class__(
            radians=v.raw,
            uncertainty=v.raw_uncertainty
        )

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        v = self.value - other.value
        return self.__class__(
            radians=v.raw,
            uncertainty=v.raw_uncertainty
        )

    def __rsub__(self, other):
        return self.__sub__(other)

    def __mul__(self, other):
        v = self.value * other.value
        return self.__class__(
            radians=v.raw,
            uncertainty=v.raw_uncertainty
        )

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        v = self.value / other.value
        return self.__class__(
            radians=v.raw,
            uncertainty=v.raw_uncertainty
        )

    def __rtruediv__(self, other):
        return self.__truediv__(other)

    def __div__(self, other):
        return self.__truediv__(other)

    def __rdiv__(self, other):
        return self.__rtruediv__(other)

    def __repr__(self):
        return self.__str__()

    def __unicode__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.value.label)

    def __str__(self):
        return '{}'.format(self.__unicode__())
