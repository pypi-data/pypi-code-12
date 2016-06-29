import py.test

import cva
import numpy as np
sa = (0.4,0.5)

assert np.isclose(cva.model.moebius(sa), (-1.0, 1.2246467991473532e-16, -0.19999999999999996)).all() 

