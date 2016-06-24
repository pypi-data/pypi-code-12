import py.test

import cva
import numpy as np


sa = (0.4,0.5)
x = cva.model.sphere(sa)

assert np.isclose((x[0]),  (0.95105651629515353, 0.0, 0.30901699437494745)).all()
