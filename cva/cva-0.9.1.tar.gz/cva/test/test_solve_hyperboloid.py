import py.test


import cva
import numpy as np
cva.solve.select(cva.model.hyperboloid,cva.metric.distance)

sa = (0.9,0.0)   # (u,v)
sb = (0.1,0.3)   # (u,v)

steps = 1
path = cva.solve.run(sa,sb,steps,silent=True)
path_length = cva.solve.path_integral(path)
assert np.isclose(path_length, 4.208749879979304) 
