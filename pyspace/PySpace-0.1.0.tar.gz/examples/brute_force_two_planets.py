#!usr/bin/env python
from pyspace.planet import PlanetArray
from pyspace.simulator import BruteForceSimulator
import pandas as pd
import numpy

x = numpy.array([0,100])
y = numpy.array([0,0])
z = numpy.array([0,0])

m = numpy.array([1000,1])

v_y = numpy.array([0,(1000/100)**0.5])

pa = PlanetArray(x, y, z, v_y=v_y, m=m)

sim = BruteForceSimulator(pa, 1, dt=1, sim_name = "two_planets")

columns = ["Time step", "Total Energy"]
values = []

for i in range(0,100,5):
    values.append([i,pa.total_energy(1)])
    sim.simulate(5, dump_output = False)

data = pd.DataFrame(data=values, columns=columns)

f = open("error_large_dt.txt", "w")

f.write(data.to_latex())

#sim.simulate(100, dump_output = True)

#print pa.dist(0,1)

