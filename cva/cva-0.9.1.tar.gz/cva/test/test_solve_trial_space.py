import py.test

import cva
import numpy as np

cva.solve.select(cva.model.earth,cva.metric.distance)

sa = (0.5,0.5)   # (u,v) a point on the equator
sb = (1.0,0.5)   # (u,v) a point at the south pole

cva.solve.set_parm('tp_max_trials',2)
cva.solve.set_parm('trace_minpoint',True)
sm = cva.solve.minpoint(sa,sb)
log = cva.solve.get_parm('log_minpoint')
(sm,trial_space,trial_integral,radius) = log[1]

assert type(log)  == list
assert len(log) == cva.solve.get_parm('tp_max_trials')
assert type(log[0][0]) == np.ndarray

assert all(sm ==  (0.75,0.5))
assert np.shape(trial_space) == (5,2)
assert np.shape(trial_integral) == (5,)
assert np.isclose(trial_integral[2], 9746.9707466596374)
assert np.isclose(radius,0.0625)

