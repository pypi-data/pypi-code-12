import py.test

import cva
import numpy as np

sa = (0.5,0.4)

assert np.isclose(cva.model.cylinder(sa), (-0.80901699437494734, 0.58778525229247325, 0.5)).all()

