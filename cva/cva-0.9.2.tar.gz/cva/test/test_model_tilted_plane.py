import py.test

import cva
import numpy as np
sa = (0.4,0.5)

assert np.isclose(cva.model.tilted_plane(sa), (0.4, 0.35355339059327379, 0.35355339059327373)).all()
