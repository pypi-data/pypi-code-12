#!usr/bin/env python
from pyspace.planet import PlanetArray
from pyspace.simulator import BarnesSimulator
import numpy

x = numpy.array([0,100])
y = numpy.array([0,0])
z = numpy.array([0,0])

m = numpy.array([1000,1])

v_y = numpy.array([0,(1000/100)**0.5])

pa = PlanetArray(x, y, z, v_y=v_y, m=m)

sim = BarnesSimulator(pa, 1, 1, 0, sim_name = "two_planets")

sim.simulate(1000, dump_output = True)

