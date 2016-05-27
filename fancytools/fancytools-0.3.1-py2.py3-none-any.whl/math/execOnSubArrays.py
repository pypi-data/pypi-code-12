import numpy as np


def execOnSubArrays(arrs, fn, splitX, splitY):
    '''
    execute a function(on or multiple arrays)
    only on sub sections 
    works only on 2d arrays at the moment

    >>> a1 = np.ones((1000,1000))
    >>> a2 = np.ones((1000,1000))
    >>> out = execOnSubArrays((a1,a2), lambda sa1,sa2: sa1+as2, splitX=10, splitY=10)

    '''
    if type(arrs) not in (tuple, list):
        arrs = (arrs,)
    s0,s1 = arrs[0].shape
    ss0 = s0 / splitX
    ss1 = s1 / splitY
    px, py = 0, 0
    out = None
    for ix in xrange(splitX):
        if ix == splitX-1:
            ss0 = s0-px

        for iy in xrange(splitY):
            if iy == splitY-1:
                ss1 = s1-py
            #current sub arrays:
            sarrs = [a[px:px+ss0, py:py+ss1] for a in arrs]
            sub = fn(*tuple(sarrs))

            if out is None:
                out = np.empty(shape=(s0, s1), dtype=sub.dtype)

            out[px:px+ss0, py:py+ss1] = sub

            py += ss1
        py = 0
        px += ss0
    return out
