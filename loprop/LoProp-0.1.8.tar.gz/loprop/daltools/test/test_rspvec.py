import unittest
import os
import numpy as np
from nose.tools import raises
from .. import rspvec, sirifc

class TestRspVec(unittest.TestCase):

    def setUp(self):
        n, e = os.path.splitext(__file__)
        self.tmpdir = n + ".d"
        self.RSPVEC = os.path.join(self.tmpdir, 'RSPVEC')
        self.SIRIFC = os.path.join(self.tmpdir, 'SIRIFC')
        self.E3VEC = os.path.join(self.tmpdir, 'E3VEC')
        self.ifc = sirifc.sirifc(name=self.SIRIFC)

    def test_read(self):
        Nx = rspvec.read("XDIPLEN", propfile=self.RSPVEC)["XDIPLEN"]
        this = Nx[12]
        ref = -0.75732690
        self.assertAlmostEqual(this, ref)

    def test_read_w(self):
        Nx = rspvec.read("XDIPLEN", freqs=(0.5,), propfile=self.RSPVEC)[("XDIPLEN", 0.5)]
        this = Nx[12]
        ref = -2.242435
        self.assertAlmostEqual(this, ref)

    def test_read_e3(self):
        Nx = rspvec.read("XDIPLEN XDIPLEN", propfile=self.E3VEC)["XDIPLEN XDIPLEN"]
        this = Nx[1]
        ref = 0.03874785
        self.assertAlmostEqual(this, ref)

    def test_read_e3_w(self):
        Nx = rspvec.read("XDIPLEN XDIPLEN", freqs=(0.5,), propfile=self.E3VEC)[("XDIPLEN XDIPLEN",0.5)]
        this = Nx[1]
        ref = 0.05668560
        self.assertAlmostEqual(this, ref)

    @raises(rspvec.RspVecError)
    def test_read_missing(self):
        Nx = rspvec.read("WRONGLAB", propfile=self.RSPVEC)

    def test_read_all(self):
        N1, N2 = rspvec.readall("XDIPLEN", self.RSPVEC)[:4:2]
        f1, f2 = N1[1], N2[1]
        self.assertListEqual([f1, f2], [0, 0.5])
        this = (N1[0][12], N2[0][12])
        ref = (-0.75732690, -2.242435)
        np.testing.assert_almost_equal(this, ref)

    def test_tomat(self):
        Nx = rspvec.read("XDIPLEN", propfile=self.RSPVEC)["XDIPLEN"]
        kx = rspvec.tomat(Nx, self.ifc, tmpdir=self.tmpdir)
        this = kx[8, 3]
        ref = 0.75732690
        self.assertAlmostEqual(this, ref)

    def test_tovec(self):
        Nx = rspvec.read("XDIPLEN", propfile=self.RSPVEC)["XDIPLEN"]
        kx = rspvec.tomat(Nx, self.ifc, tmpdir=self.tmpdir)
        Nx = rspvec.tovec(kx, self.ifc, tmpdir=self.tmpdir)
        this = Nx[44]
        ref = 0.75732690
        self.assertAlmostEqual(this, ref)

    def test_jwop(self):
        this = list(rspvec.jwop(self.ifc))
        ref = [ (i, j) for i in range(8) for j in range(8, 12)]
        self.assertListEqual(this, ref)

if __name__ == "__main__":
    unittest.main()
