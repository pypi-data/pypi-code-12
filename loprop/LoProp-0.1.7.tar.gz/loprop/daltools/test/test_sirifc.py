import unittest
import os
import numpy as np
from .. import sirifc
from ..util import full

class TestSirIfc(unittest.TestCase):

    def setUp(self):
        n, _ = os.path.splitext(__file__)
        tmpdir = n + ".d"
        self.ifc = sirifc.sirifc(os.path.join(tmpdir, 'SIRIFC'))

    def test_potnuc(self):
        self.assertAlmostEqual(self.ifc.potnuc, 31.249215315972)

    def test_emy(self):
        self.assertAlmostEqual(self.ifc.emy, -143.60291282551114)

    def test_eactive(self):
        self.assertAlmostEqual(self.ifc.eactive, 0.0)

    def test_emcscf(self):
        self.assertAlmostEqual(self.ifc.emcscf, -112.353697509539)

    def test_istate(self):
        self.assertEqual(self.ifc.istate, 1)

    def test_ispin(self):
        self.assertEqual(self.ifc.ispin, 1)

    def test_nactel(self):
        self.assertEqual(self.ifc.nactel, 0)

    def test_lsym(self):
        self.assertEqual(self.ifc.lsym, 1)

    def test_nisht(self):
        self.assertEqual(self.ifc.nisht, 8)

    def test_nasht(self):
        self.assertEqual(self.ifc.nasht, 0)

    def test_nocct(self):
        self.assertEqual(self.ifc.nocct, 8)

    def test_norbt(self):
        self.assertEqual(self.ifc.norbt, 12)

    def test_nbast(self):
        self.assertEqual(self.ifc.nbast, 12)

    def test_nsym(self):
        self.assertEqual(self.ifc.nsym, 1)

    def test_cmo(self):
        ref_cmo = [
        [ -0.00052699,  -0.99261439,   -0.12383359,    0.18555802,    0.00057906,
              -0.03008591,    0.00000536,    0.00032083,   -0.00001108,    0.20197798,
                   0.00462897,    0.10720540],
        [  0.00737583,  -0.03297262,    0.27793974,   -0.57839124,   -0.00189817,
               0.09379878,   -0.00002238,   -0.00213570,    0.00006137,   -1.26291782,
                  -0.03157479,   -0.72473780],
        [ -0.00037685,   0.00007076,   -0.00917389,   -0.01405426,    0.53138733,
              -0.01951959,    0.00540824,    0.17973082,   -0.00727428,   -0.01768689,
                  -1.15622030,    0.10138895],
        [  0.00635081,  -0.00081469,    0.15845562,    0.22175581,    0.02557339,
               0.44782244,   -0.01932019,    0.01184779,    0.02598024,    0.49118117,
                  -0.08969437,   -1.14453873],
        [ -0.00020466,   0.00002680,   -0.00510450,   -0.00713962,    0.00390034,
              -0.01434825,   -0.61014756,    0.00121769,    0.82073020,   -0.01564421,
                  -0.00740689,    0.03717125],
        [ -0.99427109,  -0.00011729,   -0.21888547,   -0.10086099,   -0.00150002,
               0.09267643,    0.00000037,   -0.00014951,    0.00000067,   -0.02177132,
                  -0.00369526,   -0.11807975],
        [ -0.02609688,   0.00584164,    0.76504310,    0.43932688,    0.00767818,
              -0.49482810,   -0.00000317,    0.00076894,   -0.00000165,    0.11725264,
                   0.02605872,    0.88618237],
        [ -0.00032727,   0.00009836,    0.00980556,   -0.00978780,    0.43759234,
               0.04594957,    0.00596611,   -0.87074890,    0.00682744,    0.00985847,
                   0.32009670,    0.04484589],
        [  0.00571602,  -0.00163778,   -0.17282397,    0.16978028,    0.03133965,
              -0.67697919,   -0.02134212,   -0.05432174,   -0.02440164,   -0.19150379,
                  -0.01188891,   -0.93744620],
        [ -0.00018408,   0.00005276,    0.00556416,   -0.00546361,    0.00288612,
               0.02187416,   -0.67280762,   -0.00599799,   -0.77019821,    0.00612449,
                   0.00321443,    0.03011564],
        [ -0.00022781,   0.00650112,    0.03189527,   -0.26702488,    0.29798906,
              -0.16111049,   -0.00000260,    0.35516810,   -0.00003403,    0.89167912,
                   0.84514752,   -0.12270512],
        [ -0.00026105,   0.00649966,    0.03167323,   -0.26196797,   -0.29964271,
              -0.16250671,   -0.00000232,   -0.35940112,   -0.00003370,    0.89524480,
                  -0.84083843,   -0.06116855]
            ]
        np.testing.assert_almost_equal(self.ifc.cmo[0], ref_cmo)


if __name__ == "__main__":
    unittest.main()


