#!usr/bin/env python
from pyspace.planet import PlanetArray
from pyspace.simulator import BarnesSimulator
import numpy

mu, sigma = 0, 10
G = 0.01
m = 1
M = 10000

x = numpy.random.normal(0, sigma, 5000)
y = numpy.random.normal(0, sigma, 5000)

z = numpy.zeros_like(x)

for i in range(len(x)):
    if x[i]**2 + y[i]**2 < 100:
        if x[i] < 0:
            x[i] -= 10
        else:
            x[i] += 10

        if y[i] < 0:
            y[i] -= 10
        else:
            y[i] += 10

x[len(x)-1] = 0
y[len(x)-1] = 0

m = numpy.ones_like(x)
m[len(x)-1] = M

v_x = numpy.zeros_like(x)
v_y = numpy.zeros_like(x)

eps = 5

for i in range(len(x)-1):
    v = (G*M*((x[i]**2 + y[i]**2)**0.5)/(eps**2 + x[i]**2 + y[i]**2))**0.5
    v_x[i] = (-v*y[i]/((x[i]**2 + y[i]**2)**0.5))
    v_y[i] = (v*x[i]/((x[i]**2 + y[i]**2)**0.5))

x0 = 500

x1 = numpy.random.normal(x0, sigma, 1000)
y1 = numpy.random.normal(0, sigma, 1000)

z1 = numpy.zeros_like(x1)

for i in range(len(x1)):
    if (x1[i]-x0)**2 + y1[i]**2 < 100:
        if x1[i] < x0:
            x1[i] -= 10
        else:
            x1[i] += 10

        if y1[i] < 0:
            y1[i] -= 10
        else:
            y1[i] += 10

x1[len(x1)-1] = x0
y1[len(x1)-1] = 0

m1 = numpy.ones_like(x1)
m1[len(x1)-1] = M

v_x1 = numpy.zeros_like(x1)
v_y1 = numpy.zeros_like(y1)

for i in range(len(x1)-1):
    v = (G*M*(((x1[i]-x0)**2 + y1[i]**2)**0.5)/(eps**2 + (x1[i]-x0)**2 + y1[i]**2))**0.5
    v_x1[i] = (-v*y1[i]/(((x1[i]-x0)**2 + y1[i]**2)**0.5))
    v_y1[i] = (v*(x1[i]-x0)/(((x1[i]-x0)**2 + y1[i]**2)**0.5))
    v_x1[i] += -(G*(M+len(x))/x0)**0.5

v_x1[len(x1)-1] = -(G*(M+len(x))/x0)**0.5

pa = PlanetArray(x, y, z, v_x, v_y, m=m)

pa1 = PlanetArray(x1, y1, z1, v_x1, v_y1, m=m1)

pa.concatenate(pa1)

sim = BarnesSimulator(pa, G=G, dt=1, epsilon = eps, theta = 1.5, sim_name = "galaxy")

sim.reset()

sim.set_data(m='m')

sim.simulate(1500, dump_output = True)

