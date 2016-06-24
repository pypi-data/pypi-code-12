import py.test

import cva
import numpy as np

cva.solve.select(cva.model.earth,cva.metric.distance)

steps = 1

sa = (0.5,0.5)   # (u,v) a point on the equator
sb = (1.0,0.5)   # (u,v) a point at the south pole
path = cva.solve.run(sa,sb,steps,silent=True)
path_length = cva.solve.path_integral(path)
assert np.isclose(path_length, 9746.970746659637)

sa = (0.5,0.2)   # (u,v) a point on the equator
sb = (0.5,0.7)   # (u,v) another point at the equator
path = cva.solve.run(sa,sb,steps,silent=True)
path_length = cva.solve.path_integral(path)
assert np.isclose(path_length, 18010.07968259746)
