import unittest
import os
import numpy as np
from ..util import full
from .. import dens

class TestDens(unittest.TestCase):

    def setUp(self):
        n, _ = os.path.splitext(__file__)
        self.tmpdir = n + ".d"

    def test_h1diag(self):
        diref = full.init([
        [0.5370962 ,  0.33768834,  0.        ],
        [ 0.33768834,  0.21231469,  0.        ],
        [ 0.        ,  0.        ,  0.        ]
	])


        di, da = dens.h1diag(1, 1, filename=os.path.join(self.tmpdir, "AOONEINT"))
        np.testing.assert_almost_equal(di, diref)

    def test_Dab(self):
        na = 2; nb = 1
        C = full.unit(3)
        da, db = dens.C2Dab(C, na, nb)
        daref = full.init(
            [[1., 0., 0], 
            [0., 1., 0.], 
            [0., 0., 0.]]
            )
        dbref = full.init(
            [[1., 0., 0], 
            [0., 0., 0.], 
            [0., 0., 0.]]
            )
        np.testing.assert_almost_equal(da, daref)
        np.testing.assert_almost_equal(db, dbref)
    

if __name__ == "__main__":
    unittest.main()
