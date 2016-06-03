from __future__ import print_function
from __future__ import absolute_import


from time import time
import pyorcy
from .compute import f


def timef(n, use_cython):
    pyorcy.USE_CYTHON = use_cython
    t1 = time()
    v = f(n, n)
    delta = time() - t1
    return delta, v


def test_compute():
    n = 1000
    t1, v1 = timef(n, False)
    t2, v2 = timef(n, True)
    assert t1 > 10 * t2   # speed-up should be at least 10x (typically 300x)
    assert v1 == v2
