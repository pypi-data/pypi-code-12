import unittest
import os
import numpy as np
from ..lr import LR

class TestLR(unittest.TestCase):

    def setUp(self):
        n, _ = os.path.splitext(__file__)
        self.tmpdir = n + ".d"

    def test_XX(self):
        XX = LR('XDIPLEN', 'XDIPLEN', 0, self.tmpdir)
        XXref = -2.461169664950
        self.assertAlmostEqual(XX, XXref)

    def test_YY(self):
        YY = LR('YDIPLEN', 'YDIPLEN', 0, self.tmpdir)
        YYref = -6.184500121159
        self.assertAlmostEqual(YY, YYref)

    def test_YZ(self):
        YZ = LR('YDIPLEN', 'ZDIPLEN', 0, self.tmpdir)
        YZref = 0.016158638023
        self.assertAlmostEqual(YZ, YZref)

    def test_ZZ(self):
        ZZ = LR('ZDIPLEN', 'ZDIPLEN', 0, self.tmpdir)
        ZZref = -10.308181624834
        self.assertAlmostEqual(ZZ, ZZref)

if __name__ == "__main__":
    unittest.main()
