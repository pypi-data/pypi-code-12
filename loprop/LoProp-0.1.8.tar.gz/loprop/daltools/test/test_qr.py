# 2014.02.26 13:49:28 CET
import os
import pdb
import numpy as np
from ..qr import QR

def assert_(this, ref):
    assert np.allclose(this, ref)



def setup():
    global tmpdir
    (n, e,) = os.path.splitext(__file__)
    tmpdir = n + '.d'



def test_XXX_A2():
    XXX = QR('XDIPLEN', 'XDIPLEN', 'XDIPLEN', tmpdir=tmpdir, a2test=True)
    XXXref = 9.652e-05
    assert_(XXX, XXXref)



def test_XXX():
    XXX = QR('XDIPLEN', 'XDIPLEN', 'XDIPLEN', tmpdir=tmpdir)
    XXXref = 0.00013323
    assert_(XXX, XXXref)

def test_ZXX():
    ZXX = QR('ZDIPLEN', 'XDIPLEN', 'XDIPLEN', tmpdir=tmpdir)
    ZXXref = -1.68075251
    assert_(ZXX, ZXXref)

def test_XZX():
    XZX = QR('XDIPLEN', 'ZDIPLEN', 'XDIPLEN', tmpdir=tmpdir)
    XZXref = -1.68075251
    assert_(XZX, XZXref)

def test_XXZ():
    XXZ = QR('XDIPLEN', 'XDIPLEN', 'ZDIPLEN', tmpdir=tmpdir)
    XXZref = -1.68075251
    assert_(XXZ, XXZref)


if __name__ == '__main__':
    setup()

#+++ okay decompyling test_qr.pyc 
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2014.02.26 13:49:28 CET
