#!/usr/bin/env python
''' Example of dumping 3d output variables.'''

import optparse
import numpy as np
from puq import dump_hdf5

# this is our random  parameter
usage = "usage: %prog --alpha a"
parser = optparse.OptionParser(usage)
parser.add_option("--alpha", type=float)
(options, args) = parser.parse_args()
a = options.alpha

# evaluate our equation over a 4x4 array
m = np.arange(1, 5)
m = np.outer(m, m)
f = (m/a)**2
dump_hdf5('f', f)

