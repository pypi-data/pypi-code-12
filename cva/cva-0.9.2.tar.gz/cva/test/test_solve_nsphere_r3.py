import py.test

import cva
import numpy as np

cva.solve.select(cva.model.sphere,cva.metric.distance)

sa = (0.5,0.5)   # (u,v) a point on the equator
sb = (1.0,0.5)   # (u,v) a point at the south pole

steps = 1
path = cva.solve.run(sa,sb,steps,silent=True)
path_length = cva.solve.path_integral(path)
assert np.isclose(path_length, 1.5307337294603591)
