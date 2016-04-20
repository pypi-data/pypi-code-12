import numpy as np


def popvar(x):
    n = len(x)
    return np.var(x, ddof=1) * (n - 1) / n

def popsd(x):

    return np.sqrt(popvar(x))
