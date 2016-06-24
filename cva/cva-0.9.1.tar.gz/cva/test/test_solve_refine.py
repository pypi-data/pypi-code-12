import py.test

import cva
import numpy as np

cva.solve.select(cva.model.earth,cva.metric.distance)

sa = (0.5,0.5)   # (u,v) a point on the equator
sb = (1.0,0.5)   # (u,v) a point at the south pole

cva.solve.set_parm('trace_refine',True)
steps = 2
path = cva.solve.run(sa,sb,steps,silent=True)
log = cva.solve.get_parm('log_refine')

assert type(log)  == list
assert len(log) == steps
assert type(log[0][2]) == np.ndarray

assert (path == log[1][2]).all()
assert np.isclose(cva.solve.path_integral(log[0][2],1), 9746.97074666)
assert np.isclose(cva.solve.path_integral(log[1][2],2), 9937.93063332)
