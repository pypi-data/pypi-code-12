import numpy as np
from transformation import *


def areCongruent(f1, f2, eps=0.001):
    """Return True if given figures are congruent, otherwise False.
    
    
    Keyword arguments:
    f1 -- the first figure
    f2 -- the second figure
    eps -- epsilon value for floating-point math (default 0.001)
    """
    allAreTransformations = isTransformation(f1) and isTransformation(f2)
    noneAreTransformations = not isTransformation(f1) or isTransformation(f2)
    
    if allAreTransformations:
        return all(areCongruent(e1, e2, eps) for e1, e2 in zip(f1, f2))
    elif noneAreTransformations:
        ratios = []
        for e1, e2 in zip(f1, f2):
            if e1 and e2:
                ratios.append(e1 / e2)
            elif e1 or e2:
                return False
        return all(abs(ratio - ratios[0]) < eps for ratio in ratios)
    else:
        return False
