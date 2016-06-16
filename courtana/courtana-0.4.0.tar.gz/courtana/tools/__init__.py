import numpy as np

from .oneeurofilter import OneEuroFilter


__all__ = ['OneEuroFilter']


def wrap_angles(a):
    """Wrap an array of angles to the interval [-pi, pi).
    """
    return (a + np.pi) % (2 * np.pi) - np.pi
