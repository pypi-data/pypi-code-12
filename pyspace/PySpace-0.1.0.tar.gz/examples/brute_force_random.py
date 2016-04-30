#!usr/bin/env python
from pyspace.planet import PlanetArray
from pyspace.simulator import BruteForceSimulator
import numpy

x = numpy.random.random_integers(0,500,500)
y = numpy.random.random_integers(0,500,500)
z = numpy.random.random_integers(0,500,500)

pa = PlanetArray(x, y, z)

sim = BruteForceSimulator(pa, 1, 1, sim_name = "random")

sim.simulate(1000, dump_output = True)

