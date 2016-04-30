#!usr/bin/env python
import numpy
from pyspace.planet import PlanetArray

class Benchmark(object):
    def __init__(self):
        x, y, z = numpy.mgrid[0:500:25j, 0:500:25j, 0:500:25j]
        self.x = x.ravel()
        self.y = y.ravel()
        self.z = z.ravel()
        self.pa = PlanetArray(x=self.x, y=self.y, z=self.z)


