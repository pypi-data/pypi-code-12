import py.test

import cva
import numpy as np

cva.solve.select(cva.model.torus,cva.metric.distance)

sa = (0.3,0.2)   # (u,v)
sb = (0.5,0.5)   # (u,v)
    
steps = 1
path = cva.solve.run(sa,sb,steps,silent=True)
path_length = cva.solve.path_integral(path)
assert np.isclose(path_length, 4.659514759363107)
