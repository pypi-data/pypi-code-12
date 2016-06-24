# -*- coding: utf-8 -*-
import py.test

import cva
import numpy as np

# latitude = 0, longitude = 0
sa = cva.model.latlon(0.0,0.0)
assert sa == (0.5,0.5)
assert np.isclose(cva.model.earth(sa), (6378.1369999999997, 0.0, 3.905482530786651e-13)).all()

# latitude = 0, longitude = 90
sa = cva.model.latlon(0.0, 90.0)
assert sa == (0.5,0.75)
assert np.isclose(cva.model.earth(sa), (3.905482530786651e-13, 6378.1369999999997, 3.905482530786651e-13)).all()

# north pole 
sa = cva.model.latlon(90.0, 0.0)
assert sa == (0.0,0.5)
assert np.isclose(cva.model.earth(sa), (0.0, 0.0, 6356.8947570813589)).all()

# south pole 
sa = cva.model.latlon(-90.0, 0.0)
assert sa == (1.0,0.5)
assert np.isclose(cva.model.earth(sa), (7.7849508167762779e-13, 0.0, -6356.8947570813589)).all()

# ETSU University, Johnson City, TN USA
lat = 36.303181
lon = -82.368280
sa = cva.model.latlon(lat, lon)
assert np.isclose(cva.model.earth(sa), (681.83360545018047, -5088.6141452168167, 3771.8036785343388)).all()

# Universidad Estatal de Bolívar, Guanujo, Bolivar, Ecuador
lat = -1.571453
lon = -79.007122
sa = cva.model.latlon(lat, lon)
assert np.isclose(cva.model.earth(sa), (1215.7671723814665, -6258.7333476397052, -174.91097626096132)).all()
