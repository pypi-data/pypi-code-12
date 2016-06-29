import py.test

import cva
import numpy as np

sa = (0.4,0.5)

# call model with tuple 
assert np.isclose(cva.model.vertical_plane(sa)[0], (0.4,  0. ,  0.5)).all()

# call model with list
assert np.isclose(cva.model.vertical_plane([0.4,0.5]), (0.4,0.0,0.5)).all()

# call model with ndarray

arr = np.asarray(sa)
assert np.isclose(cva.model.vertical_plane(arr), (0.4,0.0,0.5)).all()

# call model with row oriented array
arr = np.asarray(sa).reshape(1,-1)
assert np.isclose(cva.model.vertical_plane(arr), (0.4,0.0,0.5)).all()
