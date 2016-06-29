import py.test

import cva
import numpy as np

sa = (0.5,0.4)

assert np.isclose(cva.model.hyperboloid(sa), (0.80901699437494745, -0.58778525229247303, 0.0)).all()

