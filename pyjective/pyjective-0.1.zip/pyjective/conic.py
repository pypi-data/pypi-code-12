from collections import namedtuple
from itertools import combinations_with_replacement
import numpy as np
import np_helpers
import math
import transformation


#Conic = namedtuple('Conic', ['a', 'b', 'c', 'f', 'g', 'h'], verbose = False)


def toCoefficients(e):
    """Return the coefficients of a projective conic.
    
    Keyword arguments:
    e -- a projective conic in matrix format
    """
    
    # a, f, and h are found on the diagonal.
    a, f, h = np.diag(e)
    
    # b/2, c/2, and g/2 can be found above the diagonal.
    b, c, g = 2 * np.array(e)[np.triu_indices(3, 1)]
    
    return np.array((a, b, c, f, g, h))


def toMatrix(coeffs):
    """Given coefficients of a projective conic, return a corresponding matrix.
    
    Keyword arguments:
    coeffs -- a sequence containing the coefficients of a projective conic
    """
    a, b, c, f, g, h = coeffs
    return np.matrix(
        [[    a, b / 2, c / 2],
         [b / 2,     f, g / 2],
         [c / 2, g / 2,     h]]
    )

def fromFivePoints(p1, p2, p3, p4, p5):
    """Return the projective conic defined by the given points.
    
    Keyword arguments:
    p1 -- the first point
    p2 -- the second point
    p3 -- the third point
    p4 -- the fourth point
    p5 -- the fifth point
    """
    a = [[u * v for u, v in combinations_with_replacement(p, 2)]
         for p in p1, p2, p3, p4, p5]
    return np_helpers.nullspace(a).flatten()

def threePointsToStandard(e, p, q, r):
    """Return a projective transformation that maps three points on a conic to
the conic xy + yz + xz = 0.
    
    Keyword arguments:
    e -- a projective conic
    p -- the first point on e
    q -- the second point on e
    r -- the third point on e
    """
    coeffs = e
    p, q, r = np.matrix(p), np.matrix(q), np.matrix(r)
    
    # Determine a matrix A associated with a projective transformation that
    # maps P, Q, and R onto [1, 0, 0], [0, 1, 0], and [0, 0, 1], respectively.
    A = np.linalg.inv(np.vstack([p, q, r]))
    
    # Determine the equation bx'y' + fx'z' + gy'z' = 0 of t(E), for some real
    # numbers b, f, and g.
    M = sum([coeff * u.T * v
             for coeff, (u, v)
             in zip(coeffs, combinations_with_replacement((p, q, r), 2))])
    
    # Get B from M by adding like terms to find b, f, and g and then
    # constructing a diagonal matrix from the flat [1/g, 1/f, 1/b].
    B = np.diagflat([1 / (u + v)
                    for u, v
                    in reversed(zip(np.array(M)[np.triu_indices(3, 1)],
                                    np.array(M)[np.tril_indices(3, -1)]))])
    
    return B * A


def mapToStandard(e):
    """Return a projective transformation that maps a projective conic to the
standard conic x^2 + y^2 = z^2.
    
    Keyword arguments:
    e -- a projective conic
    """
    
    # Find a matrix A associated with E.
    a = toMatrix(e)
    
    # Find an orthogonal matrix P such that (P^T)AP is diagonal.
    eigs, p = np.linalg.eig(a)
    
    # Find the associated matrix B for t: [x] |-> [B(P^T)x].
    b = np.diagflat([math.sqrt(abs(eig)) for eig in eigs])
    return b * p.T
    

def mapThreePoints(e1, p1, q1, r1, e2, p2, q2, r2):
    """Return a projective transformation that maps three points on a conic to
three points on another conic.
    
    Keyword arguments:
    e1 -- a projective conic
    p1 -- the first point on e1
    q1 -- the second point on e1
    r1 -- the third point on e1
    e2 -- a projective conic
    p2 -- the first point on e2
    q2 -- the second point on e2
    r2 -- the third point on e2
    """
    t1 = threePointsToStandard(e1, p1, q1, r1)
    t2 = threePointsToStandard(e2, p2, q2, r2)
    return compose(np.linalg.inv(t2), t1)
