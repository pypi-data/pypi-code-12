import py.test

import cva
import numpy as np

sa = (0.1,0.1)

assert np.isclose(cva.model.capped_cylinder(sa), (-0.6472135954999579, -0.4702282018339786, 0.0)).all()

sa = (0.4,0.5)

assert np.isclose(cva.model.capped_cylinder(sa), (1.0, 0.0, 0.3666666666666667)).all()
