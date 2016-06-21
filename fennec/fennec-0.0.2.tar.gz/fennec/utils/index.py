import numpy as np

from .array import as_vector


def r2(true, pred):
    t, y = as_vector(true, pred)
    return 1 - (np.square(y - t).mean() / t.var())


def rmse(true, pred):
    t, y = as_vector(true, pred)
    return np.sqrt(np.square(y - t).mean())


def mse(true, pred):
    t, y = as_vector(true, pred)
    return np.square(y - t).mean()


def mae(true, pred):
    t, y = as_vector(true, pred)
    return np.abs(y - t).mean()
