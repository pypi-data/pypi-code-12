"""
Matrix normalization methods (primarily for expression data).
"""

import numpy as np
import pandas as pd

from wrenlab.util import matrix_transformer

def vsn(X):
    """
    Variance-stabilizing normalization.

    Arguments
    ---------
    X : :class:`pandas.DataFrame`
        An expression matrix, with probes as rows and samples as columns.

    Returns
    -------
    A :class:`pandas.DataFrame` containing the VSN normalized 
    expression values.
    """
    import wrenlab.R
    return wrenlab.R.vsn(X)

def vsn2(X):
    import wrenlab.R
    params = wrenlab.R.fit_rocke_durbin(X, theta=0.5)
    print(params)
    alpha = params["alpha"]
    v_eta = params["sd_eta"] ** 2
    v_epsilon = params["sd_epsilon"] ** 2
    S2_eta = np.exp(v_eta) * (np.exp(v_eta) - 1)
    c = v_epsilon / S2_eta

    Xm = np.array(X)
    return pd.DataFrame(np.log(Xm - alpha + np.sqrt((Xm - alpha)**2 + c)),
            index=X.index, columns=X.columns)

@matrix_transformer
def quantile(X, mu=None):
    """
    Quantile normalize a matrix.

    Parameters
    ----------
    X : a 2D :class:`numpy.ndarray`
        The matrix to be normalized, with samples as columns
        and probes/genes as rows.
    mu : a 1D :class:`numpy.ndarray`, optional
        Vector of gene means.

    Returns
    -------
    :class:`numpy.ndarray`
        The normalized matrix.
    """
    # transposed, so samples are rows
    assert not np.isnan(X).all(axis=1).any() # rows
    if mu is not None:
        mu = np.array(mu)
        assert len(mu) == X.shape[1] 
        assert not np.isnan(mu).any()
    else:
        assert not np.isnan(X).all(axis=0).any() # columns

    Xm = np.ma.masked_invalid(X.T)
    Xn = np.empty(Xm.shape)
    Xn[:] = np.nan

    if mu is None:
        mu = Xm.mean(axis=0)
    mu.sort()

    for i in range(Xm.shape[0]):
        # sort and argsort sorts small to large with NaN at the end
        ix = np.argsort(Xm[i,:])
        nok = (~Xm[i,:].mask).sum()
        ix = ix[:nok]
        rix = (np.arange(nok) * len(mu) / nok).round().astype(int)
        Xn[i,ix] = mu[rix]

    Xn = Xn.T
    assert (np.isnan(X) == np.isnan(Xn)).all()
    return Xn
