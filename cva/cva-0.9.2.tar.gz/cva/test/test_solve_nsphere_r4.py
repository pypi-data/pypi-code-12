import py.test

import cva
import numpy as np

cva.solve.select(cva.model.sphere,cva.metric.distance)

ndim = 4
sa = np.linspace(0.1,0.3,ndim-1)
sb = np.linspace(0.5,0.7,ndim-1)

steps = 1
path = cva.solve.run(sa,sb,steps,silent=True)
path_length = cva.solve.path_integral(path)
assert np.isclose(path_length, 1.6967013865209915) 

