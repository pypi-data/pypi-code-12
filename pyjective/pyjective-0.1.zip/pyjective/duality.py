from collections import namedtuple
import numpy as np


# Note: duality module only explores duality in RP^3.


def areCollinear(c1, c2, c3):
    """Return True if given points/lines are incident, otherwise False.
    
    Keyword arguments:
    c1 -- the first point/line
    c2 -- the second point/line
    c3 -- the third point/line
    """
    return np.linalg.det([c1, c2, c3]) == 0


areConcurrent = areCollinear


def containingLine(c1, c2):
    """Return the point/line incident with the provided lines/points.
    
    Keyword arguments:
    c1 -- the first point/line
    c2 -- the second point/line
    """
    return np.cross(c1, c2)


pointOfConcurrence = containingLine
