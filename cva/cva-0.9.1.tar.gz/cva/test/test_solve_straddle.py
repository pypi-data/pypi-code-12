import py.test

import cva
import numpy as np

s = np.array([(0.4,0.5),(0,0),(0.0,0.0),(0.0), (0.6,0.7)])
cva.solve.select(cva.model.sphere,cva.metric.distance)
step = 2
path = cva.solve.straddle(s,step)
assert np.isclose(path[1][0], 0.44807917531044594)



cva.solve.select(cva.model.earth,cva.metric.distance)

sa = (0.5,0.5)   # (u,v) a point on the equator
sb = (1.0,0.5)   # (u,v) a point at the south pole

cva.solve.set_parm('trace_straddle',True)
cva.solve.set_parm('tp_straddles', 2)
steps = 2
path = cva.solve.run(sa,sb,steps,silent=True)
log = cva.solve.get_parm('log_straddle')

assert type(log)  == list
assert len(log) == 4
assert type(log[3][1]) == np.ndarray
assert (path == log[3][1]).all()


