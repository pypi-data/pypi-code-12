import py.test

import cva
from cva.model import latlon
import numpy as np

cva.solve.select(cva.model.earth,cva.metric.distance)

path = cva.solve.run(latlon(-10,-170),latlon(10,170),2,silent=True)
path_length = cva.solve.path_integral(path)

assert np.isclose(path_length, 3138.453735141841)


