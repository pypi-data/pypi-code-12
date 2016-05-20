import numpy as np
from np_helpers import *


def isTransformation(lst):
    """Return True if lst is matrix-like and square.
    
    Keyword arguments:
    lst -- a Python list.
    """
    return all(isArrayLike(row) and len(row) == len(lst) for row in lst)


def findTf(q1, q2=None):
    """Finds a projective transformation from q1 to q2 or from q1 to the
    triangle of reference.
    
    
    Keyword arguments:
    q1 -- the first quadrilateral
    q2 -- the second quadrilateral (default None)
    """
    if q2:
        return findTf(q2).composite(inv(findTf(q1)))
    else:
        x = np.linalg.solve(np.matrix(q1[:-1]).T, np.matrix(q1[-1]).T)
        return np.multiply(q1[:-1], x).T


def inv(A):
    """Returns a numpy matrix representing the inverse of A.
    
    Keyword arguments:
    A -- a square numpy matrix or a square list of lists
    """
    return np.linalg.inv(A)


def transform(x, A):
    """Returns the figure x transformed by A.
    
    Keyword arguments:
    x -- a projective figure
    A -- a transformation matrix
    """
    return np.dot(A, x)


def compose(A1, A2):
    """Returns the composition A1 of A2.
    
    Keyword arguments:
    A1 -- the first transformation matrix
    A2 -- the second transformation matrix
    """
    return np.dot(A1, A2)
