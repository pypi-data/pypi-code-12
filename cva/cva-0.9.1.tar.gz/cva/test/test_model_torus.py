import py.test

import cva
import numpy as np

sa = (0.4,0.5)

assert np.isclose(cva.model.torus(sa)[0], (2.8090169943749475, 0.0, -0.58778525229247303)).all()
