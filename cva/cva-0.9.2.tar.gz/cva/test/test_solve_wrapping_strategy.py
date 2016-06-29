import py.test

import cva
import numpy as np

cva.solve.select(cva.model.sphere,cva.metric.distance)

# verify that the model returns valid results around a wrappable boundary
sa_original = np.asarray((0.5,0.001))  # a point just east of the "dateline"
sb = np.asarray((0.5,0.999))  # a point just west of the "dateline"
sm_original = (sb-sa_original)/2.0+sa_original
sa_extended = np.asarray((0.5,1.001))  # a wrapped point just east of the "dateline"
sm_extended = (sb-sa_extended)/2.0+sa_extended

dist1 = cva.metric.distance(sa_original,sm_original)
dist2 = cva.metric.distance(sa_extended,sm_extended)

assert np.isclose(cva.metric.distance(sa_original,sb), 0.012566287931118254)
assert np.isclose(cva.metric.distance(sa_extended,sb), 0.01256628793111712)

# poorly chosen path:
assert np.isclose(cva.metric.distance(sm_original,sb), 1.9999901304037162)

# well chosen path:
assert np.isclose(cva.metric.distance(sm_extended,sb), 0.00628317497175918)

# After we are finished with choose_path(), this test should pass:

path = cva.solve.run(sa_original,sb,2,silent=True)
dist_original = cva.solve.path_integral(path)
assert np.isclose(dist_original, 0.012566365446646249) 

path = cva.solve.run(sa_extended,sb,2,silent=True)
dist_extended = cva.solve.path_integral(path)
assert np.isclose(dist_extended, dist_original)
