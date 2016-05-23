"""

This module contains types useful in 2D geometry.


"""

from collections import namedtuple
from math import sqrt


class V2(namedtuple('P2', 'x y')):
    """
    2D Euclidean vector type.

    Several operations are supported.  In the following, *u* is a V2,
    *v* is either a V2 or a tuple of length 2, and *a* is a number.

    *  *u* == *v* : standard equality test.
    *  *u* + *v* :        vector addition
    *  *u* - *v* :        vector subtraction
    *  *u* * *a* or *a* * *u* :        scalar multiplication
    *  *u* / *a* :        scalar division
    *  *u* // *a* :        scalar floor division
    *  *u* @ *v* :        dot product
    """

    @property
    def length(self):
        """
        Euclidean length of this vector.
        """
        if not hasattr(self, '_length'):
            self._length = sqrt(self.x ** 2 + self.y ** 2)
        return self._length

    def __eq__(self, other):
        return self.x == other[0] and self.y == other[1]

    def __add__(self, other):
        assert isinstance(other, tuple)
        return V2(self.x + other[0], self.y + other[1])

    def __neg__(self):
        return V2(-self.x, -self.y)

    def __sub__(self, other):
        assert isinstance(other, tuple)
        return V2(self.x - other[0], self.y - other[1])

    def __mul__(self, scalar):
        return V2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar):
        return V2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return V2(self.x / scalar, self.y / scalar)

    def __floordiv__(self, scalar):
        """Scalar floor division."""
        return V2(self.x // scalar, self.y // scalar)

    def __matmul__(self, other):
        """Dot product"""
        assert isinstance(other, tuple)
        return self.x * other[0] + self.y * other[1]

    def dot(self, other):
        """Dot product (other can be a V2 or a tuple)."""
        assert isinstance(other, tuple)
        return self.x * other[0] + self.y * other[1]

    @property
    def rnormal(self):
        """right-handed normal vector (points to the right of this direction
        vector.
        """
        return V2(self.y, -self.x)

    @property
    def lnormal(self):
        """left-handed normal vector (points to the right of this direction
        vector.
        """
        return V2(-self.y, self.x)

    @property
    def unit(self):
        """Returns a normalized version of this vector (unit vector)."""
        if not hasattr(self, '_unit'):
            self._unit = V2(self.x / self.length, self.y / self.length)
        return self._unit

    def __str__(self):
        return "({0},{1})".format(self.x, self.y)


class RI(namedtuple('RI', 'min max')):
    """
    Real Interval

    .. py:method:: __new__

    .. py:attribute:: min

        lower bound.

    .. py:attribute:: max

        upper bound.

    .. describe:: x in interval

        Determine if x lies inside interval: min <= x <= max
    """

    @property
    def length(self):
        """        length of this interval"""
        return self.max - self.min

    def __contains__(self, v):
        return self.min <= v <= self.max


class Box2(namedtuple('BBox', 'xr yr')):
    """
    Axis-aligned bounding box.
    :members:
    :undoc-members:
    :inherited-members:

    .. attribute:: xr, yr

        x and y intervals (instances of class RI) of this bounding box.  These
        attributes are read-only.

    .. describe::  p in box

         True if the point p lies inside box.   p can be a V2 or tuple.
         A p is inside box if box.xr.min <= p.x <= box.xr.max and box.yr.min
         <= p.y <= box.yr.max

    """

    def __contains__(self, p):
        return p[0] in self.xr and p[1] in self.yr


class Shape2:
    """
    This is an interface for a generic 2d shape.  It only supports one
    operation:

    .. describe p in shape::

        True if the point p lies inside this shape.

    subclasses need to implement the __contains__ member function.
    """

    def __contains__(self, p):
        pass


_Tri2 = namedtuple('_Tri2', 'v0 v1 v2 n0 n1 n2 bbox')


class Tri2(_Tri2, Shape2):
    """
    2d Triangle.
    Vertices must be supplied in counter clockwise (CCW) order.

    .. attribute:: v0, v1, v2

        Triangle vertices in counter clockwise order.  These are read-only
        attributes

    .. attribute:: n0, n1, n2

        Outward-facing edge normal vectors.  These are read-only attributes

    .. describe:: p in triangle

        True if point *p* lies inside *triangle*.  *p* can be a V2 or a tuple.

    """

    def __new__(cls, v0, v1, v2):
        if not isinstance(v0, V2):
            v0 = V2(*v0)
        if not isinstance(v1, V2):
            v1 = V2(*v1)
        if not isinstance(v2, V2):
            v2 = V2(*v2)
        ax, ay = [v0.x, v1.x, v2.x], [v0.y, v1.y, v2.y]

        return super(Tri2, cls).__new__(cls, v0, v1, v2,
                                        (v1 - v0).rnormal,
                                        (v2 - v1).rnormal,
                                        (v0 - v2).rnormal,
                                        Box2(RI(min(ax), max(ax)),
                                             RI(min(ay), max(ay))))

    def __contains__(self, p):
        if not isinstance(p, V2):
            p = V2(*p)
        if p not in self.bbox:
            return False
        if self.n0.dot(p - self.v0) > 0:
            return False
        if self.n1.dot(p - self.v1) > 0:
            return False
        if self.n2.dot(p - self.v2) > 0:
            return False
        return True


_ConvPoly2 = namedtuple('_ConvPoly2', 'vertices onorms bbox')


class ConvPoly2(_ConvPoly2, Shape2):
    """
    2d Convex Polygon
    Vertices must be supplied in counter clockwise (CCW) order.

    .. attribute:: vertices

        Triangle vertices in counter clockwise order.

    .. attribute:: onorms

        Outward-facing edge normal vectors.

    .. describe:: p in poly

        True if point *p* lies inside *poly*.  *p* can be a V2 or a tuple.


    """

    def __new__(cls, vertices):
        n = len(vertices)
        vertices = [(p if isinstance(p, V2) else V2(*p)) for p in vertices]
        ax, ay = ([p.x for p in vertices], [p.y for p in vertices])
        bbox = Box2(RI(min(ax), max(ax)), RI(min(ay), max(ay)))
        return super(ConvPoly2, cls).__new__(cls, vertices,
                                             [(vertices[(i + 1) % n] - vertices[
                                                 i]).rnormal for i in
                                              range(n)],
                                             bbox)

    def __contains__(self, p):
        if not isinstance(p, V2):
            p = V2(*p)
        if p not in self.bbox:
            return False
        for i in range(len(self.vertices)):
            if self.onorms[i].dot(p - self.vertices[i]) > 0:
                return False
        return True


""""""
