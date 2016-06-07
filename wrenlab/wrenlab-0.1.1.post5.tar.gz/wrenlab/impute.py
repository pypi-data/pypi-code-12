"""
Methods for imputing missing values in matrices.
"""

import math

import pandas as pd
import numpy as np

from wrenlab.util import matrix_transformer, LOG

def qPCR(X, design, controls, max_iterations=100):
    import wrenlab.R
    return wrenlab.R.impute_qPCR(X, design, controls, 
            max_iterations=max_iterations)

def kNN(X, k=None):
    """
    Impute missing values using mean of KNN.

    Arguments
    ---------
    X: :class:`pandas.DataFrame`
        The expression matrix, with probes as rows and samples as columns.

    Returns
    -------
    A :class:`pandas.DataFrame` with missing values imputed, and rows containing
    unimputable values dropped. The resulting :class:`pandas.DataFrame` will
    have no missing values and may have fewer rows.
    """
    assert isinstance(X, pd.DataFrame)
    if k is None:
        k = math.ceil(X.shape[1] * 0.1)
    assert isinstance(k, int)

    drop_threshold = int(0.25 * X.shape[1])
    X = X.dropna(axis=0, thresh=drop_threshold)
    nn = X.corr().apply(lambda r: r.sort_values(ascending=False).index).iloc[1:,:].T
    Xn = X.copy()
    for i,j in zip(*np.array(X.isnull()).nonzero()):
        mu = X.iloc[i,:].loc[nn.iloc[j,:]].dropna().iloc[:k].mean()
        Xn.iloc[i,j] = mu
    return Xn.dropna(axis=0)

@matrix_transformer
def mean(X):
    """
    Impute missing values using the mean value of the gene.

    Arguments
    ---------
    X: :class:`numpy.ndarray`
        The expression matrix, with probes as rows and samples as columns.

    Returns
    -------
    A :class:`pandas.DataFrame` with missing values imputed, and rows containing
    unimputable values dropped. The resulting :class:`pandas.DataFrame` will
    have no missing values and may have fewer rows.
    """
    Xo = X.copy()
    X = np.ma.masked_invalid(X)
    mu = X.mean(axis=1)
    for i in range(X.shape[0]):
        Xo[i,X.mask[i,:]] = mu[i]
    return Xo

@matrix_transformer
def linear_model(X, max_iterations=5, convergence=1e-8, use_subset=True):
    if use_subset:
        max_predictors = min(500, X.shape[0] - 1)
    else:
        max_predictors = None

    nt, ns = X.shape
    missing = np.isnan(X.T)
    assert not missing.all(axis=0).any()

    converged = np.zeros(nt, dtype=bool)
    converged[missing.sum(axis=0) == 0] = True
    Xi = mean(X).T

    LOG.info("Starting linear model based imputation on matrix of shape: {}".format(X.shape))
    delta_prev = 2 ** 64

    for iteration in range(max_iterations):
        Xi_next = Xi.copy()
        delta = np.zeros(nt)
        for j in (~converged).nonzero()[0]:
            ix = missing[:,j]
            train = np.delete(Xi, np.s_[j], 1)
            if max_predictors is not None:
                predictors = np.random.choice(np.arange(train.shape[1]),
                        size=max_predictors,
                        replace=False)
                train = train[:,predictors]
            beta, _, _, sv = np.linalg.lstsq(train[~ix,:], Xi[~ix,j])
            y_hat = train @ beta
            Xi_next[ix,j] = y_hat[ix]
            delta[j] = ((y_hat[ix] - Xi[ix,j]) ** 2).mean()
        converged[delta < convergence] = True
        if converged.all():
            LOG.info("Convergence after {} iterations".format(iteration + 1))
            return Xi_next.T
        else:
            LOG.debug("Iteration {}: mean delta = {}, not converged = {}"\
                    .format(
                        iteration + 1, 
                        delta[~converged].mean(), 
                        (~converged).sum()))
            Xi = Xi_next
            if (delta_prev < delta.mean()) and (max_predictors is not None):
                # 4000 predictors is where it starts to get really slow
                max_predictors = min(int(max_predictors * 1.5), 4000)
                LOG.debug("max_predictors increased to: {}".format(max_predictors))
            delta_prev = delta.mean()
    return Xi.T
