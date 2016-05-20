import numpy as np


def crossRatio(p1, p2, p3, p4):
    """Finds the cross-ratio of four points.
    
    Keyword arguments:
    p1 -- the first point
    p2 -- the second point
    p3 -- the third point
    p4 -- the fourth point
    """
    a, b = np.linalg.lstsq(np.matrix([p1, p2]).T, np.matrix(p3).T)[0]
    c, d = np.linalg.lstsq(np.matrix([p1, p2]).T, np.matrix(p4).T)[0]
    return ((b / a) / (d / c))[(0, 0)] # Unpack result from numpy matrix.
