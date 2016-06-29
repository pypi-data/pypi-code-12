import py.test

import cva
import numpy as np

sa = (0.5,0.0)   # (u,v)
sb = (0.0,0.5)   # (u,v)

cva.solve.select(cva.model.blackhole,cva.metric.schwarzschild) 
assert np.isclose(cva.metric.schwarzschild(sa,sb), 2000.7765780260854)

sa = [0.5,0.0]   # (u,v)
sb = [0.0,0.5]   # (u,v)
assert np.isclose(cva.metric.schwarzschild(sa,sb), 2000.7765780260854)

sa = np.asarray(sa)
sb = np.asarray(sb)
assert np.isclose(cva.metric.schwarzschild(sa,sb), 2000.7765780260854)
