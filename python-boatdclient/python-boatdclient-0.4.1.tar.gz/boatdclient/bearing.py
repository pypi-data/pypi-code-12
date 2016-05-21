import math


class Bearing(object):
    '''
    An angle between 0 and 360 degrees

    Examples:

    >>> Bearing(100)
    <Bearing (100.00 degrees clockwise from north) at 0x7f25e22b3710>
    >>> Bearing(100) + Bearing(100)
    <Bearing (200.00 degrees clockwise from north) at 0x7f25e22b3940>
    >>> Bearing(100) + Bearing(300)
    <Bearing (40.00 degrees clockwise from north) at 0x7f25e22b37b8>
    >>> Bearing(0) - Bearing(100)
    <Bearing (260.00 degrees clockwise from north) at 0x7f25e22b3940>
    >>> import math
    >>> Bearing.from_radians(math.pi)
    <Bearing (180.00 degrees clockwise from north) at 0x7f25e22b3828>
    >>> int(Bearing(120.4))
    120
    >>> float(Bearing(120.4))
    120.4
    '''

    def __init__(self, degrees):
        self._degrees = float(degrees % 360)

    @classmethod
    def from_radians(cls, radians):
        return cls(math.degrees(radians))

    @property
    def degrees(self):
        return self._degrees

    def __float__(self):
        return self._degrees

    def __add__(self, n):
        return Bearing(float(self) + float(n))

    def __radd__(self, n):
        return Bearing(float(self) + float(n))

    def __sub__(self, n):
        return Bearing(float(self) - float(n))

    def __rsub__(self, n):
        return Bearing(float(n) - float(self))

    def __str__(self):
        return '{0:0.2f} degrees clockwise from north'.format(self.degrees)

    def __repr__(self):
        return '<{0}.{1} ({2}) at {3}>'.format(
            self.__module__, type(self).__name__, str(self), hex(id(self)))

    def __int__(self):
        return int(self._degrees)

    def __neg__(self):
        return Bearing(-float(self))

    def __abs__(self):
        return Bearing(abs(float(self)))
