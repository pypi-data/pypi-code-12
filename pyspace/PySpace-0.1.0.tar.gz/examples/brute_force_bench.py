#!usr/bin/env python
from pyspace.planet import PlanetArray
from pyspace.simulator import BruteForceSimulator
import numpy
import time

x = numpy.random.random_integers(0,500,500)
y = numpy.random.random_integers(0,500,500)
z = numpy.random.random_integers(0,500,500)

pa = PlanetArray(x, y, z)

sim = BruteForceSimulator(pa, 1, 1, epsilon = 1, sim_name = "random")

sim.reset()

start = time.time()
sim.simulate(5, dump_output = False)
print time.time() - start

