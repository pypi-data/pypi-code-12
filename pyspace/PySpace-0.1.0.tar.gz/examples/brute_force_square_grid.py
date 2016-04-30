#!usr/bin/env python
from pyspace.planet import PlanetArray
from pyspace.simulator import BruteForceSimulator
import numpy

x, y, z = numpy.mgrid[0:500:7j, 0:500:7j, 0:500:7j]
x = x.ravel(); y = y.ravel(); z = z.ravel()

pa = PlanetArray(x, y, z)

sim = BruteForceSimulator(pa, 1, 1, sim_name = "square_grid")

sim.simulate(1000, dump_output = True)

