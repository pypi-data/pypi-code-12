"""
Linear models.
"""

import scipy.stats
import pandas as pd
import numpy as np
import statsmodels.api as sm

def mfit(Y, design, formula=None):
    """
    Fit multiple linear models, one for each row of Y.
    """
    assert Y.isnull().sum().sum() == 0
    assert Y.shape[1] == design.shape[0]
    n = Y.shape[1]

    X = np.array(design)
    parameters = design.columns
    beta, _, rank, sv = np.linalg.lstsq(X, Y.T)
    #residual = Y.T - X @ beta
    n = X.shape[0]
    X_se = X.std(axis=0) / np.sqrt(n)
    coef = pd.DataFrame(beta.T, index=Y.index, columns=parameters)
    t = coef / X_se
    p = pd.DataFrame(scipy.stats.t.sf(t.abs(), df=n-2) * 2,
            index=t.index, columns=t.columns)
    ts = t.sort_values("Hours", ascending=False)
    print(ts.head())
    print(p.loc[ts.index,:].head())
    print(p.describe())
    #print(t.head())
    #print(np.divide(beta, X.std(axis=0)))
    #t = pd.Series(beta / X.std(axis=0), index=parameters)
    #print(t)

    """
    residual = y  - X @ beta
    #r2 = (1 - residual) / ((y - y.var())
    t = pd.Series(beta / X.std(axis=0), index=parameters)
    p = scipy.stats.t.cdf(t, df=t.shape[0] - 1)
    p = pd.Series(np.minimum(p, 1-p) * 2, index=parameters)
    coef = pd.Series(beta, index=parameters)
    """
