from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math

from measurement_stats import angle
from measurement_stats import ops
from measurement_stats import value


class Point2D(object):
    """A class for..."""

    def __init__(self, x=None, y=None):
        if x is None:
            x = value.ValueUncertainty()
        if y is None:
            y = value.ValueUncertainty()

        self.x = x
        self.y = y

    @property
    def length(self):
        """ The length of the vector

        :return:
        :rtype: value.ValueUncertainty
        """
        return self.distance_from(self.__class__())

    @property
    def nonzero(self):
        return self.x.value != 0.0 or self.x.value != 0.0

    def copy_from(self, source):
        """

        :param source:
        :return:
        """

        self.x.copy(source.x)
        self.y.copy(source.y)

    def clone(self):
        """

        :return:
        """
        return self.__class__(x=self.x.clone(), y=self.y.clone())

    def invert(self):
        """ Switches the sign of the x and y values so that x = -x and y = -y.
        """
        self.x.value = -self.x.value
        self.y.value = -self.y.value

    def rotate(self, rotation_angle, origin=None):
        """ Rotates the position value by the specified angle using a standard
            2D rotation matrix formulation. If an origin Position2D instance is
            not specified the rotation will occur around the origin. Also, if
            an origin is specified, the uncertainty in that origin value will
            be propagated through to the uncertainty of the rotated result.

        :param rotation_angle:
        :param origin: (optional)
        :return:
        """

        if origin is None:
            origin = self.__class__(
                value.ValueUncertainty(0, 0),
                value.ValueUncertainty(0, 0)
            )

        a = rotation_angle.radians
        x = self.x.raw - origin.x.raw
        y = self.y.raw - origin.y.raw

        self.x.update(
            x * math.cos(a) - y*math.sin(a) + origin.x.raw,
            ops.sqrt_sum_of_squares(self.x.uncertainty, origin.x.uncertainty)
        )
        self.y.update(
            y * math.cos(a) + x*math.sin(a) + origin.y.raw,
            ops.sqrt_sum_of_squares(self.y.uncertainty, origin.y.uncertainty)
        )

        return self

    def distance_from(self, point):
        """

        :param point:
        :return:
        """

        xDelta = self.x - point.x
        yDelta = self.y - point.y
        return (xDelta*xDelta + yDelta*yDelta) ** 0.5

    def serialize(self):
        """toDict doc..."""
        return dict(
            x=self.x.serialize(),
            y=self.y.serialize()
        )

    def normalize(self):
        """normalize doc..."""
        length = self.length
        if length == 0.0:
            return False

        self.x /= length
        self.y /= length

        return True

    def angle_between(self, point):
        """

        :param point:
        :return:
        """

        my_length = self.length
        pos_length = point.length
        numerator = self.x*point.x + self.y*point.y
        denominator = my_length * pos_length

        if value.equivalent(denominator.value, 0.0, 1e-6):
            return angle.Angle(radians=0.0, uncertainty=0.5*math.pi)

        result = numerator/denominator

        if value.equivalent(result.value, 1.0, 1e-5):
            return angle.Angle()

        try:
            if value.equivalent(result.value, -1.0, 1e-5):
                a = math.pi
            else:
                a = math.acos(result.raw)
        except Exception:
            print('[ERROR]: Unable to calculate angle between', result)
            return angle.Angle()

        if value.equivalent(a, math.pi, 1e-5):
            return angle.Angle(radians=a, uncertainty_degrees=180.0)

        try:
            aUnc = abs(1.0 / (1.0 - result.raw * result.raw) ** 0.5) * \
                   result.raw_uncertainty
        except Exception as err:
            print('[ERROR]: Unable to calculate angle between uncertainty',
                  result, a)
            return angle.Angle()

        return angle.Angle(radians=a, uncertainty=aUnc)

    def __pow__(self, power, modulo=None):
        try:
            return self.__class__(
                x=self.x ** power.x,
                y=self.y ** power.y
            )
        except Exception:
            return self.__class__(
                x=self.x ** power,
                y=self.y ** power
            )

    def __add__(self, other):
        try:
            return self.__class__(
                x=self.x + other.x,
                y=self.y + other.y
            )
        except Exception:
            return self.__class__(
                x=self.x + other,
                y=self.y + other
            )

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        try:
            return self.__class__(
                x=self.x - other.x,
                y=self.y - other.y
            )
        except Exception:
            return self.__class__(
                x=self.x - other,
                y=self.y - other
            )

    def __rsub__(self, other):
        try:
            return self.__class__(
                x=other.x - self.x,
                y=other.y - self.y
            )
        except Exception:
            return self.__class__(
                x=other - self.x,
                y=other - self.y
            )

    def __mul__(self, other):
        try:
            return self.__class__(x=self.x*other.x, y=self.y*other.y)
        except Exception:
            return self.__class__(x=self.x*other, y=self.y*other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        try:
            return self.__class__(x=self.x/other.x, y=self.y/other.y)
        except Exception:
            return self.__class__(x=self.x/other, y=self.y/other)

    def __rtruediv__(self, other):
        return self.__truediv__(other)

    def __div__(self, other):
        return self.__truediv__(other)

    def __rdiv__(self, other):
        return self.__rtruediv__(other)

    def __repr__(self):
        return self.__str__()

    def __unicode__(self):
        return '<{} {} {}>'.format(
            self.__class__.__name__,
            self.x.label,
            self.y.label
        )

    def __str__(self):
        return '{}'.format(self.__unicode__())




