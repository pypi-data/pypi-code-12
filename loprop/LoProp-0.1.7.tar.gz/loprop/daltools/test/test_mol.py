import unittest
import os
import sys
from .. import mol


class MolTest(unittest.TestCase):

    def setUp(self):
        pwd = os.path.dirname(__file__)
        dalton_bas = os.path.join(pwd, 'test_mol.d', 'DALTON.BAS')
        self.bas = mol.readin(dalton_bas)
        self.maxDiff = None

    def tearDown(self):
        pass

    def test_pass(self):
        pass

    def test_dist(self):
        self.assertAlmostEqual(
            mol.dist(self.bas[0]["center"][0], self.bas[1]["center"][0]),
            2.2852428069
            )

    def test_num(self):
        self.assertAlmostEqual(mol.nuc(self.bas), 31.2492153162)

    def test_opa(self):
        self.assertListEqual(
            mol.occupied_per_atom(self.bas),
            [[0, 1, 2, 3, 4], [0, 1, 2, 3,4], [0], [0]]
            )

    def test_cpa(self):
        self.assertListEqual(
            mol.contracted_per_atom(self.bas),
            [5, 5, 1, 1]
            )

    def test_cpal(self):
        self.assertListEqual(
            mol.contracted_per_atom_l(self.bas),
            [[2, 3], [2, 3], [1], [1]]
            )

    def test_print_atoms(self):
        output = """\
Atom type 1 charge 6.000000
center 1 [1.74063211e-05, 0.0010502765856, -1.1458244562083]
s-functions
    71.616837 [0.15432897, 0.0]
    13.045096 [0.53532814, 0.0]
    3.5305122 [0.44463454, 0.0]
    2.9412494 [0.0, -0.09996723]
    0.6834831 [0.0, 0.39951283]
    0.2222899 [0.0, 0.70011547]
p-functions
    2.9412494 [0.15591627]
    0.6834831 [0.60768372]
    0.2222899 [0.39195739]
Atom type 2 charge 8.000000
center 1 [0.0, 0.0010582718101, 1.1394183506149]
s-functions
    130.70932 [0.15432897, 0.0]
    23.808861 [0.53532814, 0.0]
    6.4436083 [0.44463454, 0.0]
    5.0331513 [0.0, -0.09996723]
    1.1695961 [0.0, 0.39951283]
    0.380389 [0.0, 0.70011547]
p-functions
    5.0331513 [0.15591627]
    1.1695961 [0.60768372]
    0.380389 [0.39195739]
Atom type 3 charge 1.000000
center 1 [-7.11056897e-05, 1.7705033753955, -2.2396975555016]
center 2 [-6.98661118e-05, -1.7998043816988, -2.2005635940297]
s-functions
    3.4252509 [0.15432897]
    0.6239137 [0.53532814]
    0.1688554 [0.44463454]"""
        mol.printbasis(self.bas)
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        print_output = sys.stdout.getvalue().strip()
        self.assertEqual(print_output, output)


        

if __name__ == "__main__":
    unittest.main()
