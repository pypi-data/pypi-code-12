import unittest
import os
import numpy as np
from .. import one
from ..util import blocked, full

class TestOne(unittest.TestCase):

    def setUp(self):
        n, _ = os.path.splitext(__file__)
        self.tmpdir = n + ".d"
        self.aooneint = os.path.join(self.tmpdir, 'AOONEINT')
        self.header = one.readhead(self.aooneint)

    def test_header_title(self):
        self.assertIn(b"CH2O", self.header["ttitle"])

    def test_header_naos(self):
        self.assertTupleEqual(self.header["naos"], (12,))

    def test_header_nsym(self):
        self.assertEqual(self.header["nsym"], 1)

    def test_header_potnuc(self):
        self.assertAlmostEqual(self.header["potnuc"], 31.249215316217)

    def test_isordk_nucdep(self):
        isordk = one.readisordk(self.aooneint)
        self.assertEqual(isordk["nucdep"], 4)
    
    def test_isordk_chrn(self):
        isordk = one.readisordk(self.aooneint)
        self.assertTupleEqual(isordk["chrn"][:3], (6., 8., 1.))

    def test_isordk_cooo(self):
        isordk = one.readisordk(self.aooneint)
        C = [-3.0015786160, -1.4563174382, 0.0550080378]
        O = [-3.1314330364, 0.8240509816, -0.0184248297]
        H1 = [-1.1728925345, -2.4468589606, 0.1025195320]
        H2 = [-4.7395143797, -2.6116033945, 0.0761219478]
        np.testing.assert_almost_equal(isordk["cooo"][0::120], C)
        np.testing.assert_almost_equal(isordk["cooo"][1::120], O)
        np.testing.assert_almost_equal(isordk["cooo"][2::120], H1)
        np.testing.assert_almost_equal(isordk["cooo"][3::120], H2)

    def test_scfinp(self):
        scfinp = one.readscfinp(self.aooneint)
        self.assertEqual(scfinp["nsym"], 1)
        coor_angstrom = (
            -1.588367, -.770650, .029109, -1.657083, .436069, -.009750, -.620668, -1.294822, .054251, -2.508043, -1.382001, .040282
            )
        coor_bohr = [ i/0.52917721 for i in coor_angstrom ]
        np.testing.assert_almost_equal(scfinp["cooo"], coor_bohr)

    def test_overlap(self):
        Sref = full.triangular.init([
    1.00000000,
    0.24836239,   1.00000000,
    0.00000000,   0.00000000,   1.00000000,
    0.00000000,   0.00000000,   0.00000000,   1.00000000,
    0.00000000,   0.00000000,   0.00000000,   0.00000000,   1.00000000,
    0.00000126,   0.03708896,  -0.00354693,   0.06228751,  -0.00200579,   1.00000000,
    0.03664911,   0.36526353,  -0.02523128,   0.44308559,  -0.01426833,   0.23670394,   1.00000000,
    0.00349314,   0.01832934,   0.21019458,   0.02979663,  -0.00095952,   0.00000000,   0.00000000,   1.00000000,
   -0.06134287,  -0.32188081,   0.02979663,  -0.31136609,   0.01685004,   0.00000000,   0.00000000,   0.00000000,   1.00000000,
    0.00197538,   0.01036527,  -0.00095952,   0.01685004,   0.21134872,   0.00000000,   0.00000000,   0.00000000,   0.00000000,   1.00000000,
    0.06072046,   0.48453953,   0.40747211,  -0.22071478,   0.01058662,   0.00476429,   0.07308063,   0.04174833,  -0.06972286,   0.00257806,   1.00000000,
    0.06021809,   0.48250496,  -0.38496913,  -0.25590672,   0.00467693,   0.00488694,   0.07467580,  -0.03512957,  -0.07505408,   0.00206544,   0.14255017,   1.00000000
    ])


        S = one.read("OVERLAP", self.aooneint)
        np.testing.assert_almost_equal(S.subblock[0], Sref)

if __name__ == "__main__":
    unittest.main()
