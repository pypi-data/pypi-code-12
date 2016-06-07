import functools

import numpy as np
import pandas as pd

from .net import download
from .memoize import memoize
from .kvstore import KVStore
from .log import LOG
from .pandas import *

###################
# Utility functions
###################

def to(t, x):
    try:
        return t(x)
    except:
        return np.nan

def as_float(x):
    return to(float, x)

def chunks(it, size=1000):
    """
    Divide an iterator into chunks of specified size. A
    chunk size of 0 means no maximum chunk size, and will
    therefore return a single list.
    
    Returns a generator of lists.
    """
    if size == 0:
        yield list(it)
    else:
        chunk = []
        for elem in it:
            chunk.append(elem)
            if len(chunk) == size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk

def matrix_transformer(fn):
    """
    A decorator for a function that takes a 2D ndarray or DataFrame as
    its only positional argument (kwargs are allowed) and returns a 
    2D ndarray of the same size.

    If a :class:`pandas.DataFrame` was supplied, this decorator will
    wrap the output 2D array by adding the appropriate labels.
    """
    @functools.wraps(fn)
    def wrap(Xi, **kwargs):
        assert len(Xi.shape) == 2
        if isinstance(Xi, pd.DataFrame):
            Xim = np.array(Xi)
            Xo = fn(Xim, **kwargs)
            assert (Xi.shape == Xo.shape)
            o = pd.DataFrame(Xo, index=Xi.index, columns=Xi.columns)
            o.index.name = Xi.index.name
            o.columns.name = Xi.columns.name
            return o
        elif isinstance(Xi, np.ndarray):
            return fn(Xi, **kwargs)
        else:
            raise ValueError
    return wrap

def ranks(xs):
    """
    Return a zero-indexed array containing the ranks of each item in xs, 
    ordered from smallest to largest.

    Arguments
    ---------
    xs : array-like, 1D

    Returns
    -------
    A :class:`numpy.ndarray` containing the ranks of each item in xs, 
    ordered from smallest to largest.
    """
    o = np.empty(xs.shape[0], dtype=np.uint64)
    o[np.argsort(xs)] = np.arange(xs.shape[0], dtype=np.uint64)
    return o

class CaseInsensitiveDict(dict):
    def __setitem__(self, key, value):
        key = key.lower()
        dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        key = key.lower()
        return dict.__getitem__(self, key)
