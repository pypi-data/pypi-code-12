import py.test

import cva
import numpy as np

sa = (0.0,0.5)   # (u,v) a point on the equator
sb = (0.5,1.0)   # (u,v) a point at the south pole

cva.solve.select(cva.model.sphere,cva.metric.distance) 

assert np.isclose(cva.metric.distance(sa,sb), 1.414213562373095)
   
sa = (0.0,0.5)
sb = (0.5,2.0)
assert np.isclose(cva.metric.distance(sa,sb), 1.414213562373095)

