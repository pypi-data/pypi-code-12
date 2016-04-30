#!/usr/bin/env python
from pyspace.planet import PlanetArray
from benchmark import Benchmark

class PlanetArrayBenchmark(Benchmark):
    def __init__(self):
        Benchmark.__init__(self)

    def time_planet_array(self):
        pa = PlanetArray(x=self.x, y=self.y, z=self.z)

    def time_dist(self):
        self.pa.dist(0,1)


