import py.test

import cva
import numpy as np

sa = (0.4,0.5)

assert np.isclose(cva.model.sphylinder(sa), (0.97522126530093345, 0.0, 0.5558929702514211)).all()
