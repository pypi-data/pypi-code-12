"""
Distance metrics and nearest neighbors functions.
"""

import pandas as pd
import numpy as np

import wrenlab.correlation

import multiprocessing as mp
import multiprocessing.sharedctypes

class SharedArray(object):
    def __init__(self, X):
        self.size = X.size
        self.shape = X.shape
        self.buffer = multiprocessing.sharedctypes.RawArray("d", X)

    @property
    def data(self):
        X = np.ctypeslib.as_array(self.buffer)
        X.shape = self.shape
        return X

def _nearest_neighbors(X, i, k):
    r = wrenlab.correlation.pearson(X, X[i,:])["r"]
    d = np.array(1 - (r * 2))
    return np.argsort(d)[1:(k+1)]

from joblib import Parallel, delayed
from joblib.pool import has_shareable_memory

def nearest_neighbors(X, k=50):
    """
    Arguments
    ---------
    X : :class:`pandas.DataFrame`
        The expression matrix of dimensions (n,p), 
        with probes as rows and samples as columns.

    k : int, default 100
       The number of nearest neighbors. 

    Returns
    -------
    A :class:`pandas.DataFrame` of dimensions, (n,k) containing 
    the nearest neighbors.
    """
    assert k < (X.shape[0] - 1)
    assert X.T.isnull().sum().max() >= 3
    index = X.index
    X = np.array(X)
    N = np.zeros((X.shape[0], k), dtype=index.dtype)
    rs = Parallel(n_jobs=mp.cpu_count() - 2, max_nbytes=20e9)(
            delayed(_nearest_neighbors)(X, i, k) for i in range(X.shape[0]))
    for i,ix in enumerate(rs):
        N[i,:] = index[ix]
    return pd.DataFrame(N, index=index)
