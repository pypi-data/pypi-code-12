import unittest
import os
import numpy as np
from ..lr import LR

class TestOpenLR(unittest.TestCase):

    def setUp(self):
        n, _ = os.path.splitext(__file__)
        self.tmpdir = n + ".d"

    def test_XX(self):
        XX = LR('XDIPLEN', 'XDIPLEN', 0, self.tmpdir)
        XXref = -5.455606903637
        self.assertAlmostEqual(XX, XXref)

    def test_YY(self):
        YY = LR('YDIPLEN', 'YDIPLEN', 0, self.tmpdir)
        YYref = -10.31180304740
        self.assertAlmostEqual(YY, YYref)

    def test_YZ(self):
        YZ = LR('YDIPLEN', 'ZDIPLEN', 0, self.tmpdir)
        YZref = 0.2324294799056
        self.assertAlmostEqual(YZ, YZref)

    def test_ZZ(self):
        ZZ = LR('ZDIPLEN', 'ZDIPLEN', 0, self.tmpdir)
        ZZref = -3.124432068117
        self.assertAlmostEqual(ZZ, ZZref)

if __name__ == "__main__":
    unittest.main()
