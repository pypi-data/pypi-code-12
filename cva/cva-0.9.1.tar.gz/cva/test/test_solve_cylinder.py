import py.test


import cva
import numpy as np

cva.solve.select(cva.model.cylinder,cva.metric.distance)

#sa = (0.5,0.0)   # (u,v)
#sb = (1.0,0.9)   # (u,v)

# new conventions where u is "latitude"
# and v is a periodic "longitude"

sa = (1.0,0.5)   # (u,v)
sb = (0.1,1.0)   # (u,v)

steps = 1
path = cva.solve.run(sa,sb,steps,silent=True)
path_length = cva.solve.path_integral(path)
assert np.isclose(path_length, 2.6106443589632793) 
