from collections import namedtuple
from math import sqrt


class V2(namedtuple('P2', 'x y')):
    @property
    def length(self):
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

    def __truediv__(self, scalar):
        return V2(self.x / scalar, self.y / scalar)

    def __floordiv__(self, scalar):
        return V2(self.x // scalar, self.y // scalar)

    def __rmul__(self, scalar):
        return V2(self.x * scalar, self.y * scalar)

    def __matmul__(self, other):
        assert isinstance(other, tuple)
        return self.x * other[0] + self.y * other[1]

    def dot(self, other):
        assert isinstance(other, tuple)
        return self.x * other[0] + self.y * other[1]

    @property
    def rnormal(self):
        return V2(self.y, -self.x)

    @property
    def lnormal(self):
        return V2(-self.y, self.x)

    @property
    def unit(self):
        if not hasattr(self, '_unit'):
            self._unit = V2(self.x / self.length, self.y / self.length)
        return self._unit

    def __str__(self):
        return "({0},{1})".format(self.x, self.y)


class Iv(namedtuple('Iv', 'min max')):
    @property
    def length(self):
        return self.max - self.min

    def __contains__(self, v):
        return self.min <= self.max


class Box2(namedtuple('BBox', 'x_range y_range')):
    def __contains__(self, p):
        return p[0] in self.x_range and p[1] in self.y_range


class Shape2:
    def __contains__(self, p):
        pass


_Tri2 = namedtuple('_Tri2', 'v0 v1 v2 n0 n1 n2 bbox')


class Tri2(_Tri2, Shape2):
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
                                        Box2(Iv(min(ax), max(ax)),
                                             Iv(min(ay), max(ay))))

    def __contains__(self, p):
        if not isinstance(p, V2):
            p = V2(*p)
        if p not in self.bbox:
            return False
        if self.n0 @ (p - self.v0) > 0:
            return False
        if self.n1 @ (p - self.v1) > 0:
            return False
        if self.n2 @ (p - self.v2) > 0:
            return False
        return True


_ConvPoly2 = namedtuple('_ConvPoly2', 'vertices inorms bbox')


class ConvPoly2(_ConvPoly2, Shape2):
    def __new__(cls, vertices):
        n = len(vertices)
        vertices = [(p if isinstance(p, V2) else V2(*p)) for p in vertices]
        ax, ay = ([p.x for p in vertices], [p.y for p in vertices])
        bbox = Box2(Iv(min(ax), max(ax)), Iv(min(ay), max(ay)))
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
            if self.inorms[i] @ (p - self.vertices[i]) > 0:
                return False
        return True


""""""
