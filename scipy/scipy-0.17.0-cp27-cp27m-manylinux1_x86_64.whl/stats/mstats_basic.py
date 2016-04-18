"""
An extension of scipy.stats.stats to support masked arrays

"""
# Original author (2007): Pierre GF Gerard-Marchant

# TODO : f_value_wilks_lambda looks botched... what are dfnum & dfden for ?
# TODO : ttest_rel looks botched:  what are x1,x2,v1,v2 for ?
# TODO : reimplement ksonesamp

from __future__ import division, print_function, absolute_import


__all__ = ['argstoarray',
           'betai',
           'count_tied_groups',
           'describe',
           'f_oneway','f_value_wilks_lambda','find_repeats','friedmanchisquare',
           'kendalltau','kendalltau_seasonal','kruskal','kruskalwallis',
           'ks_twosamp','ks_2samp','kurtosis','kurtosistest',
           'linregress',
           'mannwhitneyu', 'meppf','mode','moment','mquantiles','msign',
           'normaltest',
           'obrientransform',
           'pearsonr','plotting_positions','pointbiserialr',
           'rankdata',
           'scoreatpercentile','sem',
           'sen_seasonal_slopes','signaltonoise','skew','skewtest','spearmanr',
           'theilslopes','threshold','tmax','tmean','tmin','trim','trimboth',
           'trimtail','trima','trimr','trimmed_mean','trimmed_std',
           'trimmed_stde','trimmed_var','tsem','ttest_1samp','ttest_onesamp',
           'ttest_ind','ttest_rel','tvar',
           'variation',
           'winsorize',
           ]

import numpy as np
from numpy import ndarray
import numpy.ma as ma
from numpy.ma import masked, nomask

from scipy._lib.six import iteritems

import itertools
import warnings
from collections import namedtuple

from . import distributions
import scipy.special as special
from ._stats_mstats_common import (
        _find_repeats,
        linregress as stats_linregress,
        theilslopes as stats_theilslopes
        )


genmissingvaldoc = """

    Notes
    -----
    Missing values are considered pair-wise: if a value is missing in x,
    the corresponding value in y is masked.
    """


def _chk_asarray(a, axis):
    # Always returns a masked array, raveled for axis=None
    a = ma.asanyarray(a)
    if axis is None:
        a = ma.ravel(a)
        outaxis = 0
    else:
        outaxis = axis
    return a, outaxis


def _chk2_asarray(a, b, axis):
    a = ma.asanyarray(a)
    b = ma.asanyarray(b)
    if axis is None:
        a = ma.ravel(a)
        b = ma.ravel(b)
        outaxis = 0
    else:
        outaxis = axis
    return a, b, outaxis


def _chk_size(a,b):
    a = ma.asanyarray(a)
    b = ma.asanyarray(b)
    (na, nb) = (a.size, b.size)
    if na != nb:
        raise ValueError("The size of the input array should match!"
                         " (%s <> %s)" % (na, nb))
    return (a, b, na)


def argstoarray(*args):
    """
    Constructs a 2D array from a group of sequences.

    Sequences are filled with missing values to match the length of the longest
    sequence.

    Parameters
    ----------
    args : sequences
        Group of sequences.

    Returns
    -------
    argstoarray : MaskedArray
        A ( `m` x `n` ) masked array, where `m` is the number of arguments and
        `n` the length of the longest argument.

    Notes
    -----
    `numpy.ma.row_stack` has identical behavior, but is called with a sequence
    of sequences.

    """
    if len(args) == 1 and not isinstance(args[0], ndarray):
        output = ma.asarray(args[0])
        if output.ndim != 2:
            raise ValueError("The input should be 2D")
    else:
        n = len(args)
        m = max([len(k) for k in args])
        output = ma.array(np.empty((n,m), dtype=float), mask=True)
        for (k,v) in enumerate(args):
            output[k,:len(v)] = v

    output[np.logical_not(np.isfinite(output._data))] = masked
    return output


def find_repeats(arr):
    """Find repeats in arr and return a tuple (repeats, repeat_count).

    The input is cast to float64. Masked values are discarded.

    Parameters
    ----------
    arr : sequence
        Input array. The array is flattened if it is not 1D.

    Returns
    -------
    repeats : ndarray
        Array of repeated values.
    counts : ndarray
        Array of counts.

    """
    # Make sure we get a copy. ma.compressed promises a "new array", but can
    # actually return a reference.
    compr = np.asarray(ma.compressed(arr), dtype=np.float64)
    if compr is arr or compr.base is arr:
        compr = compr.copy()
    return _find_repeats(compr)


def count_tied_groups(x, use_missing=False):
    """
    Counts the number of tied values.

    Parameters
    ----------
    x : sequence
        Sequence of data on which to counts the ties
    use_missing : bool, optional
        Whether to consider missing values as tied.

    Returns
    -------
    count_tied_groups : dict
        Returns a dictionary (nb of ties: nb of groups).

    Examples
    --------
    >>> from scipy.stats import mstats
    >>> z = [0, 0, 0, 2, 2, 2, 3, 3, 4, 5, 6]
    >>> mstats.count_tied_groups(z)
    {2: 1, 3: 2}

    In the above example, the ties were 0 (3x), 2 (3x) and 3 (2x).

    >>> z = np.ma.array([0, 0, 1, 2, 2, 2, 3, 3, 4, 5, 6])
    >>> mstats.count_tied_groups(z)
    {2: 2, 3: 1}
    >>> z[[1,-1]] = np.ma.masked
    >>> mstats.count_tied_groups(z, use_missing=True)
    {2: 2, 3: 1}

    """
    nmasked = ma.getmask(x).sum()
    # We need the copy as find_repeats will overwrite the initial data
    data = ma.compressed(x).copy()
    (ties, counts) = find_repeats(data)
    nties = {}
    if len(ties):
        nties = dict(zip(np.unique(counts), itertools.repeat(1)))
        nties.update(dict(zip(*find_repeats(counts))))

    if nmasked and use_missing:
        try:
            nties[nmasked] += 1
        except KeyError:
            nties[nmasked] = 1

    return nties


def rankdata(data, axis=None, use_missing=False):
    """Returns the rank (also known as order statistics) of each data point
    along the given axis.

    If some values are tied, their rank is averaged.
    If some values are masked, their rank is set to 0 if use_missing is False,
    or set to the average rank of the unmasked values if use_missing is True.

    Parameters
    ----------
    data : sequence
        Input data. The data is transformed to a masked array
    axis : {None,int}, optional
        Axis along which to perform the ranking.
        If None, the array is first flattened. An exception is raised if
        the axis is specified for arrays with a dimension larger than 2
    use_missing : bool, optional
        Whether the masked values have a rank of 0 (False) or equal to the
        average rank of the unmasked values (True).

    """
    def _rank1d(data, use_missing=False):
        n = data.count()
        rk = np.empty(data.size, dtype=float)
        idx = data.argsort()
        rk[idx[:n]] = np.arange(1,n+1)

        if use_missing:
            rk[idx[n:]] = (n+1)/2.
        else:
            rk[idx[n:]] = 0

        repeats = find_repeats(data.copy())
        for r in repeats[0]:
            condition = (data == r).filled(False)
            rk[condition] = rk[condition].mean()
        return rk

    data = ma.array(data, copy=False)
    if axis is None:
        if data.ndim > 1:
            return _rank1d(data.ravel(), use_missing).reshape(data.shape)
        else:
            return _rank1d(data, use_missing)
    else:
        return ma.apply_along_axis(_rank1d,axis,data,use_missing).view(ndarray)


ModeResult = namedtuple('ModeResult', ('mode', 'count'))


def mode(a, axis=0):
    """
    Returns an array of the modal (most common) value in the passed array.

    Parameters
    ----------
    a : array_like
        n-dimensional array of which to find mode(s).
    axis : int or None, optional
        Axis along which to operate. Default is 0. If None, compute over
        the whole array `a`.

    Returns
    -------
    mode : ndarray
        Array of modal values.
    count : ndarray
        Array of counts for each mode.

    Notes
    -----
    For more details, see `stats.mode`.

    """
    a, axis = _chk_asarray(a, axis)

    def _mode1D(a):
        (rep,cnt) = find_repeats(a)
        if not cnt.ndim:
            return (0, 0)
        elif cnt.size:
            return (rep[cnt.argmax()], cnt.max())
        else:
            not_masked_indices = ma.flatnotmasked_edges(a)
            first_not_masked_index = not_masked_indices[0]
            return (a[first_not_masked_index], 1)

    if axis is None:
        output = _mode1D(ma.ravel(a))
        output = (ma.array(output[0]), ma.array(output[1]))
    else:
        output = ma.apply_along_axis(_mode1D, axis, a)
        newshape = list(a.shape)
        newshape[axis] = 1
        slices = [slice(None)] * output.ndim
        slices[axis] = 0
        modes = output[tuple(slices)].reshape(newshape)
        slices[axis] = 1
        counts = output[tuple(slices)].reshape(newshape)
        output = (modes, counts)

    return ModeResult(*output)


@np.deprecate(message="mstats.betai is deprecated in scipy 0.17.0; "
              "use special.betainc instead.")
def betai(a, b, x):
    """
    betai() is deprecated in scipy 0.17.0.

    For details about this function, see `stats.betai`.
    """
    return _betai(a, b, x)


def _betai(a, b, x):
    x = np.asanyarray(x)
    x = ma.where(x < 1.0, x, 1.0)  # if x > 1 then return 1.0
    return special.betainc(a, b, x)


def msign(x):
    """Returns the sign of x, or 0 if x is masked."""
    return ma.filled(np.sign(x), 0)


def pearsonr(x,y):
    """
    Calculates a Pearson correlation coefficient and the p-value for testing
    non-correlation.

    The Pearson correlation coefficient measures the linear relationship
    between two datasets. Strictly speaking, Pearson's correlation requires
    that each dataset be normally distributed. Like other correlation
    coefficients, this one varies between -1 and +1 with 0 implying no
    correlation. Correlations of -1 or +1 imply an exact linear
    relationship. Positive correlations imply that as `x` increases, so does
    `y`. Negative correlations imply that as `x` increases, `y` decreases.

    The p-value roughly indicates the probability of an uncorrelated system
    producing datasets that have a Pearson correlation at least as extreme
    as the one computed from these datasets. The p-values are not entirely
    reliable but are probably reasonable for datasets larger than 500 or so.

    Parameters
    ----------
    x : 1-D array_like
        Input
    y : 1-D array_like
        Input

    Returns
    -------
    pearsonr : float
        Pearson's correlation coefficient, 2-tailed p-value.

    References
    ----------
    http://www.statsoft.com/textbook/glosp.html#Pearson%20Correlation

    """
    (x, y, n) = _chk_size(x, y)
    (x, y) = (x.ravel(), y.ravel())
    # Get the common mask and the total nb of unmasked elements
    m = ma.mask_or(ma.getmask(x), ma.getmask(y))
    n -= m.sum()
    df = n-2
    if df < 0:
        return (masked, masked)

    (mx, my) = (x.mean(), y.mean())
    (xm, ym) = (x-mx, y-my)

    r_num = ma.add.reduce(xm*ym)
    r_den = ma.sqrt(ma.dot(xm,xm) * ma.dot(ym,ym))
    r = r_num / r_den
    # Presumably, if r > 1, then it is only some small artifact of floating
    # point arithmetic.
    r = min(r, 1.0)
    r = max(r, -1.0)
    df = n - 2

    if r is masked or abs(r) == 1.0:
        prob = 0.
    else:
        t_squared = (df / ((1.0 - r) * (1.0 + r))) * r * r
        prob = _betai(0.5*df, 0.5, df/(df + t_squared))

    return r, prob


SpearmanrResult = namedtuple('SpearmanrResult', ('correlation', 'pvalue'))


def spearmanr(x, y, use_ties=True):
    """
    Calculates a Spearman rank-order correlation coefficient and the p-value
    to test for non-correlation.

    The Spearman correlation is a nonparametric measure of the linear
    relationship between two datasets. Unlike the Pearson correlation, the
    Spearman correlation does not assume that both datasets are normally
    distributed. Like other correlation coefficients, this one varies
    between -1 and +1 with 0 implying no correlation. Correlations of -1 or
    +1 imply an exact linear relationship. Positive correlations imply that
    as `x` increases, so does `y`. Negative correlations imply that as `x`
    increases, `y` decreases.

    Missing values are discarded pair-wise: if a value is missing in `x`, the
    corresponding value in `y` is masked.

    The p-value roughly indicates the probability of an uncorrelated system
    producing datasets that have a Spearman correlation at least as extreme
    as the one computed from these datasets. The p-values are not entirely
    reliable but are probably reasonable for datasets larger than 500 or so.

    Parameters
    ----------
    x : array_like
        The length of `x` must be > 2.
    y : array_like
        The length of `y` must be > 2.
    use_ties : bool, optional
        Whether the correction for ties should be computed.

    Returns
    -------
    correlation : float
        Spearman correlation coefficient
    pvalue : float
        2-tailed p-value.

    References
    ----------
    [CRCProbStat2000] section 14.7

    """
    (x, y, n) = _chk_size(x, y)
    (x, y) = (x.ravel(), y.ravel())

    m = ma.mask_or(ma.getmask(x), ma.getmask(y))
    n -= m.sum()
    if m is not nomask:
        x = ma.array(x, mask=m, copy=True)
        y = ma.array(y, mask=m, copy=True)
    df = n-2
    if df < 0:
        raise ValueError("The input must have at least 3 entries!")

    # Gets the ranks and rank differences
    rankx = rankdata(x)
    ranky = rankdata(y)
    dsq = np.add.reduce((rankx-ranky)**2)
    # Tie correction
    if use_ties:
        xties = count_tied_groups(x)
        yties = count_tied_groups(y)
        corr_x = np.sum(v*k*(k**2-1) for (k,v) in iteritems(xties))/12.
        corr_y = np.sum(v*k*(k**2-1) for (k,v) in iteritems(yties))/12.
    else:
        corr_x = corr_y = 0

    denom = n*(n**2 - 1)/6.
    if corr_x != 0 or corr_y != 0:
        rho = denom - dsq - corr_x - corr_y
        rho /= ma.sqrt((denom-2*corr_x)*(denom-2*corr_y))
    else:
        rho = 1. - dsq/denom

    t = ma.sqrt(ma.divide(df,(rho+1.0)*(1.0-rho))) * rho
    if t is masked:
        prob = 0.
    else:
        prob = _betai(0.5*df, 0.5, df/(df + t * t))

    return SpearmanrResult(rho, prob)


KendalltauResult = namedtuple('KendalltauResult', ('correlation', 'pvalue'))


def kendalltau(x, y, use_ties=True, use_missing=False):
    """
    Computes Kendall's rank correlation tau on two variables *x* and *y*.

    Parameters
    ----------
    x : sequence
        First data list (for example, time).
    y : sequence
        Second data list.
    use_ties : {True, False}, optional
        Whether ties correction should be performed.
    use_missing : {False, True}, optional
        Whether missing data should be allocated a rank of 0 (False) or the
        average rank (True)

    Returns
    -------
    correlation : float
        Kendall tau
    pvalue : float
        Approximate 2-side p-value.

    """
    (x, y, n) = _chk_size(x, y)
    (x, y) = (x.flatten(), y.flatten())
    m = ma.mask_or(ma.getmask(x), ma.getmask(y))
    if m is not nomask:
        x = ma.array(x, mask=m, copy=True)
        y = ma.array(y, mask=m, copy=True)
        n -= m.sum()

    if n < 2:
        return KendalltauResult(np.nan, np.nan)

    rx = ma.masked_equal(rankdata(x, use_missing=use_missing), 0)
    ry = ma.masked_equal(rankdata(y, use_missing=use_missing), 0)
    idx = rx.argsort()
    (rx, ry) = (rx[idx], ry[idx])
    C = np.sum([((ry[i+1:] > ry[i]) * (rx[i+1:] > rx[i])).filled(0).sum()
                for i in range(len(ry)-1)], dtype=float)
    D = np.sum([((ry[i+1:] < ry[i])*(rx[i+1:] > rx[i])).filled(0).sum()
                for i in range(len(ry)-1)], dtype=float)
    if use_ties:
        xties = count_tied_groups(x)
        yties = count_tied_groups(y)
        corr_x = np.sum([v*k*(k-1) for (k,v) in iteritems(xties)], dtype=float)
        corr_y = np.sum([v*k*(k-1) for (k,v) in iteritems(yties)], dtype=float)
        denom = ma.sqrt((n*(n-1)-corr_x)/2. * (n*(n-1)-corr_y)/2.)
    else:
        denom = n*(n-1)/2.
    tau = (C-D) / denom

    var_s = n*(n-1)*(2*n+5)
    if use_ties:
        var_s -= np.sum(v*k*(k-1)*(2*k+5)*1. for (k,v) in iteritems(xties))
        var_s -= np.sum(v*k*(k-1)*(2*k+5)*1. for (k,v) in iteritems(yties))
        v1 = np.sum([v*k*(k-1) for (k, v) in iteritems(xties)], dtype=float) *\
             np.sum([v*k*(k-1) for (k, v) in iteritems(yties)], dtype=float)
        v1 /= 2.*n*(n-1)
        if n > 2:
            v2 = np.sum([v*k*(k-1)*(k-2) for (k,v) in iteritems(xties)],
                        dtype=float) * \
                 np.sum([v*k*(k-1)*(k-2) for (k,v) in iteritems(yties)],
                        dtype=float)
            v2 /= 9.*n*(n-1)*(n-2)
        else:
            v2 = 0
    else:
        v1 = v2 = 0

    var_s /= 18.
    var_s += (v1 + v2)
    z = (C-D)/np.sqrt(var_s)
    prob = special.erfc(abs(z)/np.sqrt(2))
    return KendalltauResult(tau, prob)


def kendalltau_seasonal(x):
    """
    Computes a multivariate Kendall's rank correlation tau, for seasonal data.

    Parameters
    ----------
    x : 2-D ndarray
        Array of seasonal data, with seasons in columns.

    """
    x = ma.array(x, subok=True, copy=False, ndmin=2)
    (n,m) = x.shape
    n_p = x.count(0)

    S_szn = np.sum(msign(x[i:]-x[i]).sum(0) for i in range(n))
    S_tot = S_szn.sum()

    n_tot = x.count()
    ties = count_tied_groups(x.compressed())
    corr_ties = np.sum(v*k*(k-1) for (k,v) in iteritems(ties))
    denom_tot = ma.sqrt(1.*n_tot*(n_tot-1)*(n_tot*(n_tot-1)-corr_ties))/2.

    R = rankdata(x, axis=0, use_missing=True)
    K = ma.empty((m,m), dtype=int)
    covmat = ma.empty((m,m), dtype=float)
    denom_szn = ma.empty(m, dtype=float)
    for j in range(m):
        ties_j = count_tied_groups(x[:,j].compressed())
        corr_j = np.sum(v*k*(k-1) for (k,v) in iteritems(ties_j))
        cmb = n_p[j]*(n_p[j]-1)
        for k in range(j,m,1):
            K[j,k] = np.sum(msign((x[i:,j]-x[i,j])*(x[i:,k]-x[i,k])).sum()
                               for i in range(n))
            covmat[j,k] = (K[j,k] + 4*(R[:,j]*R[:,k]).sum() -
                           n*(n_p[j]+1)*(n_p[k]+1))/3.
            K[k,j] = K[j,k]
            covmat[k,j] = covmat[j,k]

        denom_szn[j] = ma.sqrt(cmb*(cmb-corr_j)) / 2.

    var_szn = covmat.diagonal()

    z_szn = msign(S_szn) * (abs(S_szn)-1) / ma.sqrt(var_szn)
    z_tot_ind = msign(S_tot) * (abs(S_tot)-1) / ma.sqrt(var_szn.sum())
    z_tot_dep = msign(S_tot) * (abs(S_tot)-1) / ma.sqrt(covmat.sum())

    prob_szn = special.erfc(abs(z_szn)/np.sqrt(2))
    prob_tot_ind = special.erfc(abs(z_tot_ind)/np.sqrt(2))
    prob_tot_dep = special.erfc(abs(z_tot_dep)/np.sqrt(2))

    chi2_tot = (z_szn*z_szn).sum()
    chi2_trd = m * z_szn.mean()**2
    output = {'seasonal tau': S_szn/denom_szn,
              'global tau': S_tot/denom_tot,
              'global tau (alt)': S_tot/denom_szn.sum(),
              'seasonal p-value': prob_szn,
              'global p-value (indep)': prob_tot_ind,
              'global p-value (dep)': prob_tot_dep,
              'chi2 total': chi2_tot,
              'chi2 trend': chi2_trd,
              }
    return output


PointbiserialrResult = namedtuple('PointbiserialrResult', ('correlation',
                                                           'pvalue'))


def pointbiserialr(x, y):
    """Calculates a point biserial correlation coefficient and its p-value.

    Parameters
    ----------
    x : array_like of bools
        Input array.
    y : array_like
        Input array.

    Returns
    -------
    correlation : float
        R value
    pvalue : float
        2-tailed p-value

    Notes
    -----
    Missing values are considered pair-wise: if a value is missing in x,
    the corresponding value in y is masked.

    For more details on `pointbiserialr`, see `stats.pointbiserialr`.

    """
    x = ma.fix_invalid(x, copy=True).astype(bool)
    y = ma.fix_invalid(y, copy=True).astype(float)
    # Get rid of the missing data
    m = ma.mask_or(ma.getmask(x), ma.getmask(y))
    if m is not nomask:
        unmask = np.logical_not(m)
        x = x[unmask]
        y = y[unmask]

    n = len(x)
    # phat is the fraction of x values that are True
    phat = x.sum() / float(n)
    y0 = y[~x]  # y-values where x is False
    y1 = y[x]  # y-values where x is True
    y0m = y0.mean()
    y1m = y1.mean()

    rpb = (y1m - y0m)*np.sqrt(phat * (1-phat)) / y.std()

    df = n-2
    t = rpb*ma.sqrt(df/(1.0-rpb**2))
    prob = _betai(0.5*df, 0.5, df/(df+t*t))

    return PointbiserialrResult(rpb, prob)


LinregressResult = namedtuple('LinregressResult', ('slope', 'intercept',
                                                   'rvalue', 'pvalue',
                                                   'stderr'))


def linregress(x, y=None):
    """
    Linear regression calculation

    Note that the non-masked version is used, and that this docstring is
    replaced by the non-masked docstring + some info on missing data.

    """
    if y is None:
        x = ma.array(x)
        if x.shape[0] == 2:
            x, y = x
        elif x.shape[1] == 2:
            x, y = x.T
        else:
            msg = ("If only `x` is given as input, it has to be of shape "
                   "(2, N) or (N, 2), provided shape was %s" % str(x.shape))
            raise ValueError(msg)
    else:
        x = ma.array(x)
        y = ma.array(y)

    x = x.flatten()
    y = y.flatten()

    m = ma.mask_or(ma.getmask(x), ma.getmask(y), shrink=False)
    if m is not nomask:
        x = ma.array(x, mask=m)
        y = ma.array(y, mask=m)
        if np.any(~m):
            slope, intercept, r, prob, sterrest = stats_linregress(x.data[~m],
                                                                   y.data[~m])
        else:
            # All data is masked
            return None, None, None, None, None
    else:
        slope, intercept, r, prob, sterrest = stats_linregress(x.data, y.data)

    return LinregressResult(slope, intercept, r, prob, sterrest)

if stats_linregress.__doc__:
    linregress.__doc__ = stats_linregress.__doc__ + genmissingvaldoc


def theilslopes(y, x=None, alpha=0.95):
    r"""
    Computes the Theil-Sen estimator for a set of points (x, y).

    `theilslopes` implements a method for robust linear regression.  It
    computes the slope as the median of all slopes between paired values.

    Parameters
    ----------
    y : array_like
        Dependent variable.
    x : array_like or None, optional
        Independent variable. If None, use ``arange(len(y))`` instead.
    alpha : float, optional
        Confidence degree between 0 and 1. Default is 95% confidence.
        Note that `alpha` is symmetric around 0.5, i.e. both 0.1 and 0.9 are
        interpreted as "find the 90% confidence interval".

    Returns
    -------
    medslope : float
        Theil slope.
    medintercept : float
        Intercept of the Theil line, as ``median(y) - medslope*median(x)``.
    lo_slope : float
        Lower bound of the confidence interval on `medslope`.
    up_slope : float
        Upper bound of the confidence interval on `medslope`.

    Notes
    -----
    For more details on `theilslopes`, see `stats.theilslopes`.

    """
    y = ma.asarray(y).flatten()
    if x is None:
        x = ma.arange(len(y), dtype=float)
    else:
        x = ma.asarray(x).flatten()
        if len(x) != len(y):
            raise ValueError("Incompatible lengths ! (%s<>%s)" % (len(y),len(x)))

    m = ma.mask_or(ma.getmask(x), ma.getmask(y))
    y._mask = x._mask = m
    # Disregard any masked elements of x or y
    y = y.compressed()
    x = x.compressed().astype(float)
    # We now have unmasked arrays so can use `stats.theilslopes`
    return stats_theilslopes(y, x, alpha=alpha)


def sen_seasonal_slopes(x):
    x = ma.array(x, subok=True, copy=False, ndmin=2)
    (n,_) = x.shape
    # Get list of slopes per season
    szn_slopes = ma.vstack([(x[i+1:]-x[i])/np.arange(1,n-i)[:,None]
                            for i in range(n)])
    szn_medslopes = ma.median(szn_slopes, axis=0)
    medslope = ma.median(szn_slopes, axis=None)
    return szn_medslopes, medslope


Ttest_1sampResult = namedtuple('Ttest_1sampResult', ('statistic', 'pvalue'))


def ttest_1samp(a, popmean, axis=0):
    """
    Calculates the T-test for the mean of ONE group of scores.

    Parameters
    ----------
    a : array_like
        sample observation
    popmean : float or array_like
        expected value in null hypothesis, if array_like than it must have the
        same shape as `a` excluding the axis dimension
    axis : int or None, optional
        Axis along which to compute test. If None, compute over the whole
        array `a`.

    Returns
    -------
    statistic : float or array
        t-statistic
    pvalue : float or array
        two-tailed p-value

    Notes
    -----
    For more details on `ttest_1samp`, see `stats.ttest_1samp`.

    """
    a, axis = _chk_asarray(a, axis)
    if a.size == 0:
        return (np.nan, np.nan)

    x = a.mean(axis=axis)
    v = a.var(axis=axis, ddof=1)
    n = a.count(axis=axis)
    # force df to be an array for masked division not to throw a warning
    df = ma.asanyarray(n - 1.0)
    svar = ((n - 1.0) * v) / df
    with np.errstate(divide='ignore', invalid='ignore'):
        t = (x - popmean) / ma.sqrt(svar / n)
    prob = special.betainc(0.5*df, 0.5, df/(df + t*t))

    return Ttest_1sampResult(t, prob)
ttest_onesamp = ttest_1samp


Ttest_indResult = namedtuple('Ttest_indResult', ('statistic', 'pvalue'))


def ttest_ind(a, b, axis=0, equal_var=True):
    """
    Calculates the T-test for the means of TWO INDEPENDENT samples of scores.

    Parameters
    ----------
    a, b : array_like
        The arrays must have the same shape, except in the dimension
        corresponding to `axis` (the first, by default).
    axis : int or None, optional
        Axis along which to compute test. If None, compute over the whole
        arrays, `a`, and `b`.
    equal_var : bool, optional
        If True, perform a standard independent 2 sample test that assumes equal
        population variances.
        If False, perform Welch's t-test, which does not assume equal population
        variance.
        .. versionadded:: 0.17.0

    Returns
    -------
    statistic : float or array
        The calculated t-statistic.
    pvalue : float or array
        The two-tailed p-value.

    Notes
    -----
    For more details on `ttest_ind`, see `stats.ttest_ind`.

    """
    a, b, axis = _chk2_asarray(a, b, axis)

    if a.size == 0 or b.size == 0:
        return Ttest_indResult(np.nan, np.nan)

    (x1, x2) = (a.mean(axis), b.mean(axis))
    (v1, v2) = (a.var(axis=axis, ddof=1), b.var(axis=axis, ddof=1))
    (n1, n2) = (a.count(axis), b.count(axis))

    if equal_var:
        # force df to be an array for masked division not to throw a warning
        df = ma.asanyarray(n1 + n2 - 2.0)
        svar = ((n1-1)*v1+(n2-1)*v2) / df
        denom = ma.sqrt(svar*(1.0/n1 + 1.0/n2))  # n-D computation here!
    else:
        vn1 = v1/n1
        vn2 = v2/n2
        with np.errstate(divide='ignore', invalid='ignore'):
            df = (vn1 + vn2)**2 / (vn1**2 / (n1 - 1) + vn2**2 / (n2 - 1))

        # If df is undefined, variances are zero.
        # It doesn't matter what df is as long as it is not NaN.
        df = np.where(np.isnan(df), 1, df)
        denom = ma.sqrt(vn1 + vn2)

    with np.errstate(divide='ignore', invalid='ignore'):
        t = (x1-x2) / denom
    probs = special.betainc(0.5*df, 0.5, df/(df + t*t)).reshape(t.shape)

    return Ttest_indResult(t, probs.squeeze())


Ttest_relResult = namedtuple('Ttest_relResult', ('statistic', 'pvalue'))


def ttest_rel(a, b, axis=0):
    """
    Calculates the T-test on TWO RELATED samples of scores, a and b.

    Parameters
    ----------
    a, b : array_like
        The arrays must have the same shape.
    axis : int or None, optional
        Axis along which to compute test. If None, compute over the whole
        arrays, `a`, and `b`.

    Returns
    -------
    statistic : float or array
        t-statistic
    pvalue : float or array
        two-tailed p-value

    Notes
    -----
    For more details on `ttest_rel`, see `stats.ttest_rel`.

    """
    a, b, axis = _chk2_asarray(a, b, axis)
    if len(a) != len(b):
        raise ValueError('unequal length arrays')

    if a.size == 0 or b.size == 0:
        return Ttest_relResult(np.nan, np.nan)

    n = a.count(axis)
    df = ma.asanyarray(n-1.0)
    d = (a-b).astype('d')
    dm = d.mean(axis)
    v = d.var(axis=axis, ddof=1)
    denom = ma.sqrt(v / n)
    with np.errstate(divide='ignore', invalid='ignore'):
        t = dm / denom

    probs = special.betainc(0.5*df, 0.5, df/(df + t*t)).reshape(t.shape).squeeze()

    return Ttest_relResult(t, probs)


MannwhitneyuResult = namedtuple('MannwhitneyuResult', ('statistic',
                                                       'pvalue'))


def mannwhitneyu(x,y, use_continuity=True):
    """
    Computes the Mann-Whitney statistic

    Missing values in `x` and/or `y` are discarded.

    Parameters
    ----------
    x : sequence
        Input
    y : sequence
        Input
    use_continuity : {True, False}, optional
        Whether a continuity correction (1/2.) should be taken into account.

    Returns
    -------
    statistic : float
        The Mann-Whitney statistics
    pvalue : float
        Approximate p-value assuming a normal distribution.

    """
    x = ma.asarray(x).compressed().view(ndarray)
    y = ma.asarray(y).compressed().view(ndarray)
    ranks = rankdata(np.concatenate([x,y]))
    (nx, ny) = (len(x), len(y))
    nt = nx + ny
    U = ranks[:nx].sum() - nx*(nx+1)/2.
    U = max(U, nx*ny - U)
    u = nx*ny - U

    mu = (nx*ny)/2.
    sigsq = (nt**3 - nt)/12.
    ties = count_tied_groups(ranks)
    sigsq -= np.sum(v*(k**3-k) for (k,v) in iteritems(ties))/12.
    sigsq *= nx*ny/float(nt*(nt-1))

    if use_continuity:
        z = (U - 1/2. - mu) / ma.sqrt(sigsq)
    else:
        z = (U - mu) / ma.sqrt(sigsq)

    prob = special.erfc(abs(z)/np.sqrt(2))
    return MannwhitneyuResult(u, prob)


KruskalResult = namedtuple('KruskalResult', ('statistic', 'pvalue'))


def kruskal(*args):
    """
    Compute the Kruskal-Wallis H-test for independent samples

    Parameters
    ----------
    sample1, sample2, ... : array_like
       Two or more arrays with the sample measurements can be given as
       arguments.

    Returns
    -------
    statistic : float
       The Kruskal-Wallis H statistic, corrected for ties
    pvalue : float
       The p-value for the test using the assumption that H has a chi
       square distribution

    Notes
    -----
    For more details on `kruskal`, see `stats.kruskal`.

    """
    output = argstoarray(*args)
    ranks = ma.masked_equal(rankdata(output, use_missing=False), 0)
    sumrk = ranks.sum(-1)
    ngrp = ranks.count(-1)
    ntot = ranks.count()
    H = 12./(ntot*(ntot+1)) * (sumrk**2/ngrp).sum() - 3*(ntot+1)
    # Tie correction
    ties = count_tied_groups(ranks)
    T = 1. - np.sum(v*(k**3-k) for (k,v) in iteritems(ties))/float(ntot**3-ntot)
    if T == 0:
        raise ValueError('All numbers are identical in kruskal')

    H /= T
    df = len(output) - 1
    prob = distributions.chi2.sf(H, df)
    return KruskalResult(H, prob)
kruskalwallis = kruskal


def ks_twosamp(data1, data2, alternative="two-sided"):
    """
    Computes the Kolmogorov-Smirnov test on two samples.

    Missing values are discarded.

    Parameters
    ----------
    data1 : array_like
        First data set
    data2 : array_like
        Second data set
    alternative : {'two-sided', 'less', 'greater'}, optional
        Indicates the alternative hypothesis.  Default is 'two-sided'.

    Returns
    -------
    d : float
        Value of the Kolmogorov Smirnov test
    p : float
        Corresponding p-value.

    """
    (data1, data2) = (ma.asarray(data1), ma.asarray(data2))
    (n1, n2) = (data1.count(), data2.count())
    n = (n1*n2/float(n1+n2))
    mix = ma.concatenate((data1.compressed(), data2.compressed()))
    mixsort = mix.argsort(kind='mergesort')
    csum = np.where(mixsort < n1, 1./n1, -1./n2).cumsum()
    # Check for ties
    if len(np.unique(mix)) < (n1+n2):
        csum = csum[np.r_[np.diff(mix[mixsort]).nonzero()[0],-1]]

    alternative = str(alternative).lower()[0]
    if alternative == 't':
        d = ma.abs(csum).max()
        prob = special.kolmogorov(np.sqrt(n)*d)
    elif alternative == 'l':
        d = -csum.min()
        prob = np.exp(-2*n*d**2)
    elif alternative == 'g':
        d = csum.max()
        prob = np.exp(-2*n*d**2)
    else:
        raise ValueError("Invalid value for the alternative hypothesis: "
                         "should be in 'two-sided', 'less' or 'greater'")

    return (d, prob)
ks_2samp = ks_twosamp


@np.deprecate(message="mstats.threshold is deprecated in scipy 0.17.0")
def threshold(a, threshmin=None, threshmax=None, newval=0):
    """
    Clip array to a given value.

    Similar to numpy.clip(), except that values less than `threshmin` or
    greater than `threshmax` are replaced by `newval`, instead of by
    `threshmin` and `threshmax` respectively.

    Parameters
    ----------
    a : ndarray
        Input data
    threshmin : {None, float}, optional
        Lower threshold. If None, set to the minimum value.
    threshmax : {None, float}, optional
        Upper threshold. If None, set to the maximum value.
    newval : {0, float}, optional
        Value outside the thresholds.

    Returns
    -------
    threshold : ndarray
        Returns `a`, with values less then `threshmin` and values greater
        `threshmax` replaced with `newval`.

    """
    a = ma.array(a, copy=True)
    mask = np.zeros(a.shape, dtype=bool)
    if threshmin is not None:
        mask |= (a < threshmin).filled(False)

    if threshmax is not None:
        mask |= (a > threshmax).filled(False)

    a[mask] = newval
    return a


def trima(a, limits=None, inclusive=(True,True)):
    """
    Trims an array by masking the data outside some given limits.

    Returns a masked version of the input array.

    Parameters
    ----------
    a : array_like
        Input array.
    limits : {None, tuple}, optional
        Tuple of (lower limit, upper limit) in absolute values.
        Values of the input array lower (greater) than the lower (upper) limit
        will be masked.  A limit is None indicates an open interval.
    inclusive : (bool, bool) tuple, optional
        Tuple of (lower flag, upper flag), indicating whether values exactly
        equal to the lower (upper) limit are allowed.

    """
    a = ma.asarray(a)
    a.unshare_mask()
    if (limits is None) or (limits == (None, None)):
        return a

    (lower_lim, upper_lim) = limits
    (lower_in, upper_in) = inclusive
    condition = False
    if lower_lim is not None:
        if lower_in:
            condition |= (a < lower_lim)
        else:
            condition |= (a <= lower_lim)

    if upper_lim is not None:
        if upper_in:
            condition |= (a > upper_lim)
        else:
            condition |= (a >= upper_lim)

    a[condition.filled(True)] = masked
    return a


def trimr(a, limits=None, inclusive=(True, True), axis=None):
    """
    Trims an array by masking some proportion of the data on each end.
    Returns a masked version of the input array.

    Parameters
    ----------
    a : sequence
        Input array.
    limits : {None, tuple}, optional
        Tuple of the percentages to cut on each side of the array, with respect
        to the number of unmasked data, as floats between 0. and 1.
        Noting n the number of unmasked data before trimming, the
        (n*limits[0])th smallest data and the (n*limits[1])th largest data are
        masked, and the total number of unmasked data after trimming is
        n*(1.-sum(limits)).  The value of one limit can be set to None to
        indicate an open interval.
    inclusive : {(True,True) tuple}, optional
        Tuple of flags indicating whether the number of data being masked on
        the left (right) end should be truncated (True) or rounded (False) to
        integers.
    axis : {None,int}, optional
        Axis along which to trim. If None, the whole array is trimmed, but its
        shape is maintained.

    """
    def _trimr1D(a, low_limit, up_limit, low_inclusive, up_inclusive):
        n = a.count()
        idx = a.argsort()
        if low_limit:
            if low_inclusive:
                lowidx = int(low_limit*n)
            else:
                lowidx = np.round(low_limit*n)
            a[idx[:lowidx]] = masked
        if up_limit is not None:
            if up_inclusive:
                upidx = n - int(n*up_limit)
            else:
                upidx = n - np.round(n*up_limit)
            a[idx[upidx:]] = masked
        return a

    a = ma.asarray(a)
    a.unshare_mask()
    if limits is None:
        return a

    # Check the limits
    (lolim, uplim) = limits
    errmsg = "The proportion to cut from the %s should be between 0. and 1."
    if lolim is not None:
        if lolim > 1. or lolim < 0:
            raise ValueError(errmsg % 'beginning' + "(got %s)" % lolim)
    if uplim is not None:
        if uplim > 1. or uplim < 0:
            raise ValueError(errmsg % 'end' + "(got %s)" % uplim)

    (loinc, upinc) = inclusive

    if axis is None:
        shp = a.shape
        return _trimr1D(a.ravel(),lolim,uplim,loinc,upinc).reshape(shp)
    else:
        return ma.apply_along_axis(_trimr1D, axis, a, lolim,uplim,loinc,upinc)

trimdoc = """
    Parameters
    ----------
    a : sequence
        Input array
    limits : {None, tuple}, optional
        If `relative` is False, tuple (lower limit, upper limit) in absolute values.
        Values of the input array lower (greater) than the lower (upper) limit are
        masked.

        If `relative` is True, tuple (lower percentage, upper percentage) to cut
        on each side of the  array, with respect to the number of unmasked data.

        Noting n the number of unmasked data before trimming, the (n*limits[0])th
        smallest data and the (n*limits[1])th largest data are masked, and the
        total number of unmasked data after trimming is n*(1.-sum(limits))
        In each case, the value of one limit can be set to None to indicate an
        open interval.

        If limits is None, no trimming is performed
    inclusive : {(bool, bool) tuple}, optional
        If `relative` is False, tuple indicating whether values exactly equal
        to the absolute limits are allowed.
        If `relative` is True, tuple indicating whether the number of data
        being masked on each side should be rounded (True) or truncated
        (False).
    relative : bool, optional
        Whether to consider the limits as absolute values (False) or proportions
        to cut (True).
    axis : int, optional
        Axis along which to trim.
"""


def trim(a, limits=None, inclusive=(True,True), relative=False, axis=None):
    """
    Trims an array by masking the data outside some given limits.

    Returns a masked version of the input array.

    %s

    Examples
    --------
    >>> from scipy.stats.mstats import trim
    >>> z = [ 1, 2, 3, 4, 5, 6, 7, 8, 9,10]
    >>> print(trim(z,(3,8)))
    [-- -- 3 4 5 6 7 8 -- --]
    >>> print(trim(z,(0.1,0.2),relative=True))
    [-- 2 3 4 5 6 7 8 -- --]

    """
    if relative:
        return trimr(a, limits=limits, inclusive=inclusive, axis=axis)
    else:
        return trima(a, limits=limits, inclusive=inclusive)

if trim.__doc__ is not None:
    trim.__doc__ = trim.__doc__ % trimdoc


def trimboth(data, proportiontocut=0.2, inclusive=(True,True), axis=None):
    """
    Trims the smallest and largest data values.

    Trims the `data` by masking the ``int(proportiontocut * n)`` smallest and
    ``int(proportiontocut * n)`` largest values of data along the given axis,
    where n is the number of unmasked values before trimming.

    Parameters
    ----------
    data : ndarray
        Data to trim.
    proportiontocut : float, optional
        Percentage of trimming (as a float between 0 and 1).
        If n is the number of unmasked values before trimming, the number of
        values after trimming is ``(1 - 2*proportiontocut) * n``.
        Default is 0.2.
    inclusive : {(bool, bool) tuple}, optional
        Tuple indicating whether the number of data being masked on each side
        should be rounded (True) or truncated (False).
    axis : int, optional
        Axis along which to perform the trimming.
        If None, the input array is first flattened.

    """
    return trimr(data, limits=(proportiontocut,proportiontocut),
                 inclusive=inclusive, axis=axis)


def trimtail(data, proportiontocut=0.2, tail='left', inclusive=(True,True),
             axis=None):
    """
    Trims the data by masking values from one tail.

    Parameters
    ----------
    data : array_like
        Data to trim.
    proportiontocut : float, optional
        Percentage of trimming. If n is the number of unmasked values
        before trimming, the number of values after trimming is
        ``(1 - proportiontocut) * n``.  Default is 0.2.
    tail : {'left','right'}, optional
        If 'left' the `proportiontocut` lowest values will be masked.
        If 'right' the `proportiontocut` highest values will be masked.
        Default is 'left'.
    inclusive : {(bool, bool) tuple}, optional
        Tuple indicating whether the number of data being masked on each side
        should be rounded (True) or truncated (False).  Default is
        (True, True).
    axis : int, optional
        Axis along which to perform the trimming.
        If None, the input array is first flattened.  Default is None.

    Returns
    -------
    trimtail : ndarray
        Returned array of same shape as `data` with masked tail values.

    """
    tail = str(tail).lower()[0]
    if tail == 'l':
        limits = (proportiontocut,None)
    elif tail == 'r':
        limits = (None, proportiontocut)
    else:
        raise TypeError("The tail argument should be in ('left','right')")

    return trimr(data, limits=limits, axis=axis, inclusive=inclusive)

trim1 = trimtail


def trimmed_mean(a, limits=(0.1,0.1), inclusive=(1,1), relative=True,
                 axis=None):
    """Returns the trimmed mean of the data along the given axis.

    %s

    """ % trimdoc
    if (not isinstance(limits,tuple)) and isinstance(limits,float):
        limits = (limits, limits)
    if relative:
        return trimr(a,limits=limits,inclusive=inclusive,axis=axis).mean(axis=axis)
    else:
        return trima(a,limits=limits,inclusive=inclusive).mean(axis=axis)


def trimmed_var(a, limits=(0.1,0.1), inclusive=(1,1), relative=True,
                axis=None, ddof=0):
    """Returns the trimmed variance of the data along the given axis.

    %s
    ddof : {0,integer}, optional
        Means Delta Degrees of Freedom. The denominator used during computations
        is (n-ddof). DDOF=0 corresponds to a biased estimate, DDOF=1 to an un-
        biased estimate of the variance.

    """ % trimdoc
    if (not isinstance(limits,tuple)) and isinstance(limits,float):
        limits = (limits, limits)
    if relative:
        out = trimr(a,limits=limits, inclusive=inclusive,axis=axis)
    else:
        out = trima(a,limits=limits,inclusive=inclusive)

    return out.var(axis=axis, ddof=ddof)


def trimmed_std(a, limits=(0.1,0.1), inclusive=(1,1), relative=True,
                axis=None, ddof=0):
    """Returns the trimmed standard deviation of the data along the given axis.

    %s
    ddof : {0,integer}, optional
        Means Delta Degrees of Freedom. The denominator used during computations
        is (n-ddof). DDOF=0 corresponds to a biased estimate, DDOF=1 to an un-
        biased estimate of the variance.

    """ % trimdoc
    if (not isinstance(limits,tuple)) and isinstance(limits,float):
        limits = (limits, limits)
    if relative:
        out = trimr(a,limits=limits,inclusive=inclusive,axis=axis)
    else:
        out = trima(a,limits=limits,inclusive=inclusive)
    return out.std(axis=axis,ddof=ddof)


def trimmed_stde(a, limits=(0.1,0.1), inclusive=(1,1), axis=None):
    """
    Returns the standard error of the trimmed mean along the given axis.

    Parameters
    ----------
    a : sequence
        Input array
    limits : {(0.1,0.1), tuple of float}, optional
        tuple (lower percentage, upper percentage) to cut  on each side of the
        array, with respect to the number of unmasked data.

        If n is the number of unmasked data before trimming, the values
        smaller than ``n * limits[0]`` and the values larger than
        ``n * `limits[1]`` are masked, and the total number of unmasked
        data after trimming is ``n * (1.-sum(limits))``.  In each case,
        the value of one limit can be set to None to indicate an open interval.
        If `limits` is None, no trimming is performed.
    inclusive : {(bool, bool) tuple} optional
        Tuple indicating whether the number of data being masked on each side
        should be rounded (True) or truncated (False).
    axis : int, optional
        Axis along which to trim.

    Returns
    -------
    trimmed_stde : scalar or ndarray

    """
    def _trimmed_stde_1D(a, low_limit, up_limit, low_inclusive, up_inclusive):
        "Returns the standard error of the trimmed mean for a 1D input data."
        n = a.count()
        idx = a.argsort()
        if low_limit:
            if low_inclusive:
                lowidx = int(low_limit*n)
            else:
                lowidx = np.round(low_limit*n)
            a[idx[:lowidx]] = masked
        if up_limit is not None:
            if up_inclusive:
                upidx = n - int(n*up_limit)
            else:
                upidx = n - np.round(n*up_limit)
            a[idx[upidx:]] = masked
        a[idx[:lowidx]] = a[idx[lowidx]]
        a[idx[upidx:]] = a[idx[upidx-1]]
        winstd = a.std(ddof=1)
        return winstd / ((1-low_limit-up_limit)*np.sqrt(len(a)))

    a = ma.array(a, copy=True, subok=True)
    a.unshare_mask()
    if limits is None:
        return a.std(axis=axis,ddof=1)/ma.sqrt(a.count(axis))
    if (not isinstance(limits,tuple)) and isinstance(limits,float):
        limits = (limits, limits)

    # Check the limits
    (lolim, uplim) = limits
    errmsg = "The proportion to cut from the %s should be between 0. and 1."
    if lolim is not None:
        if lolim > 1. or lolim < 0:
            raise ValueError(errmsg % 'beginning' + "(got %s)" % lolim)
    if uplim is not None:
        if uplim > 1. or uplim < 0:
            raise ValueError(errmsg % 'end' + "(got %s)" % uplim)

    (loinc, upinc) = inclusive
    if (axis is None):
        return _trimmed_stde_1D(a.ravel(),lolim,uplim,loinc,upinc)
    else:
        if a.ndim > 2:
            raise ValueError("Array 'a' must be at most two dimensional, but got a.ndim = %d" % a.ndim)
        return ma.apply_along_axis(_trimmed_stde_1D, axis, a,
                                   lolim,uplim,loinc,upinc)


def _mask_to_limits(a, limits, inclusive):
    """Mask an array for values outside of given limits.

    This is primarily a utility function.

    Parameters
    ----------
    a : array
    limits : (float or None, float or None)
    A tuple consisting of the (lower limit, upper limit).  Values in the
    input array less than the lower limit or greater than the upper limit
    will be masked out. None implies no limit.
    inclusive : (bool, bool)
    A tuple consisting of the (lower flag, upper flag).  These flags
    determine whether values exactly equal to lower or upper are allowed.

    Returns
    -------
    A MaskedArray.

    Raises
    ------
    A ValueError if there are no values within the given limits.
    """
    lower_limit, upper_limit = limits
    lower_include, upper_include = inclusive
    am = ma.MaskedArray(a)
    if lower_limit is not None:
        if lower_include:
            am = ma.masked_less(am, lower_limit)
        else:
            am = ma.masked_less_equal(am, lower_limit)

    if upper_limit is not None:
        if upper_include:
            am = ma.masked_greater(am, upper_limit)
        else:
            am = ma.masked_greater_equal(am, upper_limit)

    if am.count() == 0:
        raise ValueError("No array values within given limits")

    return am


def tmean(a, limits=None, inclusive=(True, True), axis=None):
    """
    Compute the trimmed mean.

    Parameters
    ----------
    a : array_like
        Array of values.
    limits : None or (lower limit, upper limit), optional
        Values in the input array less than the lower limit or greater than the
        upper limit will be ignored.  When limits is None (default), then all
        values are used.  Either of the limit values in the tuple can also be
        None representing a half-open interval.
    inclusive : (bool, bool), optional
        A tuple consisting of the (lower flag, upper flag).  These flags
        determine whether values exactly equal to the lower or upper limits
        are included.  The default value is (True, True).
    axis : int or None, optional
        Axis along which to operate. If None, compute over the
        whole array. Default is None.

    Returns
    -------
    tmean : float

    Notes
    -----
    For more details on `tmean`, see `stats.tmean`.

    """
    return trima(a, limits=limits, inclusive=inclusive).mean(axis=axis)


def tvar(a, limits=None, inclusive=(True, True), axis=0, ddof=1):
    """
    Compute the trimmed variance

    This function computes the sample variance of an array of values,
    while ignoring values which are outside of given `limits`.

    Parameters
    ----------
    a : array_like
        Array of values.
    limits : None or (lower limit, upper limit), optional
        Values in the input array less than the lower limit or greater than the
        upper limit will be ignored. When limits is None, then all values are
        used. Either of the limit values in the tuple can also be None
        representing a half-open interval.  The default value is None.
    inclusive : (bool, bool), optional
        A tuple consisting of the (lower flag, upper flag).  These flags
        determine whether values exactly equal to the lower or upper limits
        are included.  The default value is (True, True).
    axis : int or None, optional
        Axis along which to operate. If None, compute over the
        whole array. Default is zero.
    ddof : int, optional
        Delta degrees of freedom. Default is 1.

    Returns
    -------
    tvar : float
        Trimmed variance.

    Notes
    -----
    For more details on `tvar`, see `stats.tvar`.

    """
    a = a.astype(float).ravel()
    if limits is None:
        n = (~a.mask).sum()  # todo: better way to do that?
        return np.ma.var(a) * n/(n-1.)
    am = _mask_to_limits(a, limits=limits, inclusive=inclusive)

    return np.ma.var(am, axis=axis, ddof=ddof)


def tmin(a, lowerlimit=None, axis=0, inclusive=True):
    """
    Compute the trimmed minimum

    Parameters
    ----------
    a : array_like
        array of values
    lowerlimit : None or float, optional
        Values in the input array less than the given limit will be ignored.
        When lowerlimit is None, then all values are used. The default value
        is None.
    axis : int or None, optional
        Axis along which to operate. Default is 0. If None, compute over the
        whole array `a`.
    inclusive : {True, False}, optional
        This flag determines whether values exactly equal to the lower limit
        are included.  The default value is True.

    Returns
    -------
    tmin : float, int or ndarray

    Notes
    -----
    For more details on `tmin`, see `stats.tmin`.

    """
    a, axis = _chk_asarray(a, axis)
    am = trima(a, (lowerlimit, None), (inclusive, False))
    return ma.minimum.reduce(am, axis)


def tmax(a, upperlimit=None, axis=0, inclusive=True):
    """
    Compute the trimmed maximum

    This function computes the maximum value of an array along a given axis,
    while ignoring values larger than a specified upper limit.

    Parameters
    ----------
    a : array_like
        array of values
    upperlimit : None or float, optional
        Values in the input array greater than the given limit will be ignored.
        When upperlimit is None, then all values are used. The default value
        is None.
    axis : int or None, optional
        Axis along which to operate. Default is 0. If None, compute over the
        whole array `a`.
    inclusive : {True, False}, optional
        This flag determines whether values exactly equal to the upper limit
        are included.  The default value is True.

    Returns
    -------
    tmax : float, int or ndarray

    Notes
    -----
    For more details on `tmax`, see `stats.tmax`.

    """
    a, axis = _chk_asarray(a, axis)
    am = trima(a, (None, upperlimit), (False, inclusive))
    return ma.maximum.reduce(am, axis)


def tsem(a, limits=None, inclusive=(True, True), axis=0, ddof=1):
    """
    Compute the trimmed standard error of the mean.

    This function finds the standard error of the mean for given
    values, ignoring values outside the given `limits`.

    Parameters
    ----------
    a : array_like
        array of values
    limits : None or (lower limit, upper limit), optional
        Values in the input array less than the lower limit or greater than the
        upper limit will be ignored. When limits is None, then all values are
        used. Either of the limit values in the tuple can also be None
        representing a half-open interval.  The default value is None.
    inclusive : (bool, bool), optional
        A tuple consisting of the (lower flag, upper flag).  These flags
        determine whether values exactly equal to the lower or upper limits
        are included.  The default value is (True, True).
    axis : int or None, optional
        Axis along which to operate. If None, compute over the
        whole array. Default is zero.
    ddof : int, optional
        Delta degrees of freedom. Default is 1.

    Returns
    -------
    tsem : float

    Notes
    -----
    For more details on `tsem`, see `stats.tsem`.

    """
    a = ma.asarray(a).ravel()
    if limits is None:
        n = float(a.count())
        return a.std(axis=axis, ddof=ddof)/ma.sqrt(n)

    am = trima(a.ravel(), limits, inclusive)
    sd = np.sqrt(am.var(axis=axis, ddof=ddof))
    return sd / np.sqrt(am.count())


def winsorize(a, limits=None, inclusive=(True, True), inplace=False,
              axis=None):
    """Returns a Winsorized version of the input array.

    The (limits[0])th lowest values are set to the (limits[0])th percentile,
    and the (limits[1])th highest values are set to the (1 - limits[1])th
    percentile.
    Masked values are skipped.


    Parameters
    ----------
    a : sequence
        Input array.
    limits : {None, tuple of float}, optional
        Tuple of the percentages to cut on each side of the array, with respect
        to the number of unmasked data, as floats between 0. and 1.
        Noting n the number of unmasked data before trimming, the
        (n*limits[0])th smallest data and the (n*limits[1])th largest data are
        masked, and the total number of unmasked data after trimming
        is n*(1.-sum(limits)) The value of one limit can be set to None to
        indicate an open interval.
    inclusive : {(True, True) tuple}, optional
        Tuple indicating whether the number of data being masked on each side
        should be rounded (True) or truncated (False).
    inplace : {False, True}, optional
        Whether to winsorize in place (True) or to use a copy (False)
    axis : {None, int}, optional
        Axis along which to trim. If None, the whole array is trimmed, but its
        shape is maintained.

    Notes
    -----
    This function is applied to reduce the effect of possibly spurious outliers
    by limiting the extreme values.

    """
    def _winsorize1D(a, low_limit, up_limit, low_include, up_include):
        n = a.count()
        idx = a.argsort()
        if low_limit:
            if low_include:
                lowidx = int(low_limit * n)
            else:
                lowidx = np.round(low_limit * n)
            a[idx[:lowidx]] = a[idx[lowidx]]
        if up_limit is not None:
            if up_include:
                upidx = n - int(n * up_limit)
            else:
                upidx = n - np.round(n * up_limit)
            a[idx[upidx:]] = a[idx[upidx - 1]]
        return a

    # We are going to modify a: better make a copy
    a = ma.array(a, copy=np.logical_not(inplace))

    if limits is None:
        return a
    if (not isinstance(limits, tuple)) and isinstance(limits, float):
        limits = (limits, limits)

    # Check the limits
    (lolim, uplim) = limits
    errmsg = "The proportion to cut from the %s should be between 0. and 1."
    if lolim is not None:
        if lolim > 1. or lolim < 0:
            raise ValueError(errmsg % 'beginning' + "(got %s)" % lolim)
    if uplim is not None:
        if uplim > 1. or uplim < 0:
            raise ValueError(errmsg % 'end' + "(got %s)" % uplim)

    (loinc, upinc) = inclusive

    if axis is None:
        shp = a.shape
        return _winsorize1D(a.ravel(), lolim, uplim, loinc, upinc).reshape(shp)
    else:
        return ma.apply_along_axis(_winsorize1D, axis, a, lolim, uplim, loinc,
                                   upinc)


def moment(a, moment=1, axis=0):
    """
    Calculates the nth moment about the mean for a sample.

    Parameters
    ----------
    a : array_like
       data
    moment : int, optional
       order of central moment that is returned
    axis : int or None, optional
       Axis along which the central moment is computed. Default is 0.
       If None, compute over the whole array `a`.

    Returns
    -------
    n-th central moment : ndarray or float
       The appropriate moment along the given axis or over all values if axis
       is None. The denominator for the moment calculation is the number of
       observations, no degrees of freedom correction is done.

    Notes
    -----
    For more details about `moment`, see `stats.moment`.

    """
    a, axis = _chk_asarray(a, axis)
    if moment == 1:
        # By definition the first moment about the mean is 0.
        shape = list(a.shape)
        del shape[axis]
        if shape:
            # return an actual array of the appropriate shape
            return np.zeros(shape, dtype=float)
        else:
            # the input was 1D, so return a scalar instead of a rank-0 array
            return np.float64(0.0)
    else:
        # Exponentiation by squares: form exponent sequence
        n_list = [moment]
        current_n = moment
        while current_n > 2:
            if current_n % 2:
                current_n = (current_n-1)/2
            else:
                current_n /= 2
            n_list.append(current_n)

        # Starting point for exponentiation by squares
        a_zero_mean = a - ma.expand_dims(a.mean(axis), axis)
        if n_list[-1] == 1:
            s = a_zero_mean.copy()
        else:
            s = a_zero_mean**2

        # Perform multiplications
        for n in n_list[-2::-1]:
            s = s**2
            if n % 2:
                s *= a_zero_mean
        return s.mean(axis)


def variation(a, axis=0):
    """
    Computes the coefficient of variation, the ratio of the biased standard
    deviation to the mean.

    Parameters
    ----------
    a : array_like
        Input array.
    axis : int or None, optional
        Axis along which to calculate the coefficient of variation. Default
        is 0. If None, compute over the whole array `a`.

    Returns
    -------
    variation : ndarray
        The calculated variation along the requested axis.

    Notes
    -----
    For more details about `variation`, see `stats.variation`.

    """
    a, axis = _chk_asarray(a, axis)
    return a.std(axis)/a.mean(axis)


def skew(a, axis=0, bias=True):
    """
    Computes the skewness of a data set.

    Parameters
    ----------
    a : ndarray
        data
    axis : int or None, optional
        Axis along which skewness is calculated. Default is 0.
        If None, compute over the whole array `a`.
    bias : bool, optional
        If False, then the calculations are corrected for statistical bias.

    Returns
    -------
    skewness : ndarray
        The skewness of values along an axis, returning 0 where all values are
        equal.

    Notes
    -----
    For more details about `skew`, see `stats.skew`.

    """
    a, axis = _chk_asarray(a,axis)
    n = a.count(axis)
    m2 = moment(a, 2, axis)
    m3 = moment(a, 3, axis)
    olderr = np.seterr(all='ignore')
    try:
        vals = ma.where(m2 == 0, 0, m3 / m2**1.5)
    finally:
        np.seterr(**olderr)

    if not bias:
        can_correct = (n > 2) & (m2 > 0)
        if can_correct.any():
            m2 = np.extract(can_correct, m2)
            m3 = np.extract(can_correct, m3)
            nval = ma.sqrt((n-1.0)*n)/(n-2.0)*m3/m2**1.5
            np.place(vals, can_correct, nval)
    return vals


def kurtosis(a, axis=0, fisher=True, bias=True):
    """
    Computes the kurtosis (Fisher or Pearson) of a dataset.

    Kurtosis is the fourth central moment divided by the square of the
    variance. If Fisher's definition is used, then 3.0 is subtracted from
    the result to give 0.0 for a normal distribution.

    If bias is False then the kurtosis is calculated using k statistics to
    eliminate bias coming from biased moment estimators

    Use `kurtosistest` to see if result is close enough to normal.

    Parameters
    ----------
    a : array
        data for which the kurtosis is calculated
    axis : int or None, optional
        Axis along which the kurtosis is calculated. Default is 0.
        If None, compute over the whole array `a`.
    fisher : bool, optional
        If True, Fisher's definition is used (normal ==> 0.0). If False,
        Pearson's definition is used (normal ==> 3.0).
    bias : bool, optional
        If False, then the calculations are corrected for statistical bias.

    Returns
    -------
    kurtosis : array
        The kurtosis of values along an axis. If all values are equal,
        return -3 for Fisher's definition and 0 for Pearson's definition.

    Notes
    -----
    For more details about `kurtosis`, see `stats.kurtosis`.

    """
    a, axis = _chk_asarray(a, axis)
    m2 = moment(a, 2, axis)
    m4 = moment(a, 4, axis)
    olderr = np.seterr(all='ignore')
    try:
        vals = ma.where(m2 == 0, 0, m4 / m2**2.0)
    finally:
        np.seterr(**olderr)

    if not bias:
        n = a.count(axis)
        can_correct = (n > 3) & (m2 is not ma.masked and m2 > 0)
        if can_correct.any():
            n = np.extract(can_correct, n)
            m2 = np.extract(can_correct, m2)
            m4 = np.extract(can_correct, m4)
            nval = 1.0/(n-2)/(n-3)*((n*n-1.0)*m4/m2**2.0-3*(n-1)**2.0)
            np.place(vals, can_correct, nval+3.0)
    if fisher:
        return vals - 3
    else:
        return vals


DescribeResult = namedtuple('DescribeResult', ('nobs', 'minmax', 'mean',
                                               'variance', 'skewness',
                                               'kurtosis'))


def describe(a, axis=0, ddof=0, bias=True):
    """
    Computes several descriptive statistics of the passed array.

    Parameters
    ----------
    a : array_like
        Data array
    axis : int or None, optional
        Axis along which to calculate statistics. Default 0. If None,
        compute over the whole array `a`.
    ddof : int, optional
        degree of freedom (default 0); note that default ddof is different
        from the same routine in stats.describe
    bias : bool, optional
        If False, then the skewness and kurtosis calculations are corrected for
        statistical bias.

    Returns
    -------
    nobs : int
        (size of the data (discarding missing values)

    minmax : (int, int)
        min, max

    mean : float
        arithmetic mean

    variance : float
        unbiased variance

    skewness : float
        biased skewness

    kurtosis : float
        biased kurtosis

    Examples
    --------
    >>> from scipy.stats.mstats import describe
    >>> ma = np.ma.array(range(6), mask=[0, 0, 0, 1, 1, 1])
    >>> describe(ma)
    DescribeResult(nobs=array(3), minmax=(masked_array(data = 0,
                 mask = False,
           fill_value = 999999)
    , masked_array(data = 2,
                 mask = False,
           fill_value = 999999)
    ), mean=1.0, variance=0.66666666666666663, skewness=masked_array(data = 0.0,
                 mask = False,
           fill_value = 1e+20)
    , kurtosis=-1.5)

    """
    a, axis = _chk_asarray(a, axis)
    n = a.count(axis)
    mm = (ma.minimum.reduce(a), ma.maximum.reduce(a))
    m = a.mean(axis)
    v = a.var(axis, ddof=ddof)
    sk = skew(a, axis, bias=bias)
    kurt = kurtosis(a, axis, bias=bias)

    return DescribeResult(n, mm, m, v, sk, kurt)


def stde_median(data, axis=None):
    """Returns the McKean-Schrader estimate of the standard error of the sample
    median along the given axis. masked values are discarded.

    Parameters
    ----------
    data : ndarray
        Data to trim.
    axis : {None,int}, optional
        Axis along which to perform the trimming.
        If None, the input array is first flattened.

    """
    def _stdemed_1D(data):
        data = np.sort(data.compressed())
        n = len(data)
        z = 2.5758293035489004
        k = int(np.round((n+1)/2. - z * np.sqrt(n/4.),0))
        return ((data[n-k] - data[k-1])/(2.*z))

    data = ma.array(data, copy=False, subok=True)
    if (axis is None):
        return _stdemed_1D(data)
    else:
        if data.ndim > 2:
            raise ValueError("Array 'data' must be at most two dimensional, "
                             "but got data.ndim = %d" % data.ndim)
        return ma.apply_along_axis(_stdemed_1D, axis, data)


SkewtestResult = namedtuple('SkewtestResult', ('statistic', 'pvalue'))


def skewtest(a, axis=0):
    """
    Tests whether the skew is different from the normal distribution.

    Parameters
    ----------
    a : array
        The data to be tested
    axis : int or None, optional
       Axis along which statistics are calculated. Default is 0.
       If None, compute over the whole array `a`.

    Returns
    -------
    statistic : float
        The computed z-score for this test.
    pvalue : float
        a 2-sided p-value for the hypothesis test

    Notes
    -----
    For more details about `skewtest`, see `stats.skewtest`.

    """
    a, axis = _chk_asarray(a, axis)
    if axis is None:
        a = a.ravel()
        axis = 0
    b2 = skew(a,axis)
    n = a.count(axis)
    if np.min(n) < 8:
        raise ValueError(
            "skewtest is not valid with less than 8 samples; %i samples"
            " were given." % np.min(n))

    y = b2 * ma.sqrt(((n+1)*(n+3)) / (6.0*(n-2)))
    beta2 = (3.0*(n*n+27*n-70)*(n+1)*(n+3)) / ((n-2.0)*(n+5)*(n+7)*(n+9))
    W2 = -1 + ma.sqrt(2*(beta2-1))
    delta = 1/ma.sqrt(0.5*ma.log(W2))
    alpha = ma.sqrt(2.0/(W2-1))
    y = ma.where(y == 0, 1, y)
    Z = delta*ma.log(y/alpha + ma.sqrt((y/alpha)**2+1))

    return SkewtestResult(Z, 2 * distributions.norm.sf(np.abs(Z)))


KurtosistestResult = namedtuple('KurtosistestResult', ('statistic',
                                                       'pvalue'))


def kurtosistest(a, axis=0):
    """
    Tests whether a dataset has normal kurtosis

    Parameters
    ----------
    a : array
        array of the sample data
    axis : int or None, optional
       Axis along which to compute test. Default is 0. If None,
       compute over the whole array `a`.

    Returns
    -------
    statistic : float
        The computed z-score for this test.
    pvalue : float
        The 2-sided p-value for the hypothesis test

    Notes
    -----
    For more details about `kurtosistest`, see `stats.kurtosistest`.

    """
    a, axis = _chk_asarray(a, axis)
    n = a.count(axis=axis)
    if np.min(n) < 5:
        raise ValueError(
            "kurtosistest requires at least 5 observations; %i observations"
            " were given." % np.min(n))
    if np.min(n) < 20:
        warnings.warn(
            "kurtosistest only valid for n>=20 ... continuing anyway, n=%i" %
            np.min(n))

    b2 = kurtosis(a, axis, fisher=False)
    E = 3.0*(n-1) / (n+1)
    varb2 = 24.0*n*(n-2.)*(n-3) / ((n+1)*(n+1.)*(n+3)*(n+5))
    x = (b2-E)/ma.sqrt(varb2)
    sqrtbeta1 = 6.0*(n*n-5*n+2)/((n+7)*(n+9)) * np.sqrt((6.0*(n+3)*(n+5)) /
                                                        (n*(n-2)*(n-3)))
    A = 6.0 + 8.0/sqrtbeta1 * (2.0/sqrtbeta1 + np.sqrt(1+4.0/(sqrtbeta1**2)))
    term1 = 1 - 2./(9.0*A)
    denom = 1 + x*ma.sqrt(2/(A-4.0))
    if np.ma.isMaskedArray(denom):
        # For multi-dimensional array input
        denom[denom < 0] = masked
    elif denom < 0:
        denom = masked

    term2 = ma.power((1-2.0/A)/denom,1/3.0)
    Z = (term1 - term2) / np.sqrt(2/(9.0*A))

    return KurtosistestResult(Z, 2 * distributions.norm.sf(np.abs(Z)))


NormaltestResult = namedtuple('NormaltestResult', ('statistic', 'pvalue'))


def normaltest(a, axis=0):
    """
    Tests whether a sample differs from a normal distribution.

    Parameters
    ----------
    a : array_like
        The array containing the data to be tested.
    axis : int or None, optional
        Axis along which to compute test. Default is 0. If None,
        compute over the whole array `a`.

    Returns
    -------
    statistic : float or array
        ``s^2 + k^2``, where ``s`` is the z-score returned by `skewtest` and
        ``k`` is the z-score returned by `kurtosistest`.
    pvalue : float or array
       A 2-sided chi squared probability for the hypothesis test.

    Notes
    -----
    For more details about `normaltest`, see `stats.normaltest`.

    """
    a, axis = _chk_asarray(a, axis)
    s, _ = skewtest(a, axis)
    k, _ = kurtosistest(a, axis)
    k2 = s*s + k*k

    return NormaltestResult(k2, distributions.chi2.sf(k2, 2))


def mquantiles(a, prob=list([.25,.5,.75]), alphap=.4, betap=.4, axis=None,
               limit=()):
    """
    Computes empirical quantiles for a data array.

    Samples quantile are defined by ``Q(p) = (1-gamma)*x[j] + gamma*x[j+1]``,
    where ``x[j]`` is the j-th order statistic, and gamma is a function of
    ``j = floor(n*p + m)``, ``m = alphap + p*(1 - alphap - betap)`` and
    ``g = n*p + m - j``.

    Reinterpreting the above equations to compare to **R** lead to the
    equation: ``p(k) = (k - alphap)/(n + 1 - alphap - betap)``

    Typical values of (alphap,betap) are:
        - (0,1)    : ``p(k) = k/n`` : linear interpolation of cdf
          (**R** type 4)
        - (.5,.5)  : ``p(k) = (k - 1/2.)/n`` : piecewise linear function
          (**R** type 5)
        - (0,0)    : ``p(k) = k/(n+1)`` :
          (**R** type 6)
        - (1,1)    : ``p(k) = (k-1)/(n-1)``: p(k) = mode[F(x[k])].
          (**R** type 7, **R** default)
        - (1/3,1/3): ``p(k) = (k-1/3)/(n+1/3)``: Then p(k) ~ median[F(x[k])].
          The resulting quantile estimates are approximately median-unbiased
          regardless of the distribution of x.
          (**R** type 8)
        - (3/8,3/8): ``p(k) = (k-3/8)/(n+1/4)``: Blom.
          The resulting quantile estimates are approximately unbiased
          if x is normally distributed
          (**R** type 9)
        - (.4,.4)  : approximately quantile unbiased (Cunnane)
        - (.35,.35): APL, used with PWM

    Parameters
    ----------
    a : array_like
        Input data, as a sequence or array of dimension at most 2.
    prob : array_like, optional
        List of quantiles to compute.
    alphap : float, optional
        Plotting positions parameter, default is 0.4.
    betap : float, optional
        Plotting positions parameter, default is 0.4.
    axis : int, optional
        Axis along which to perform the trimming.
        If None (default), the input array is first flattened.
    limit : tuple, optional
        Tuple of (lower, upper) values.
        Values of `a` outside this open interval are ignored.

    Returns
    -------
    mquantiles : MaskedArray
        An array containing the calculated quantiles.

    Notes
    -----
    This formulation is very similar to **R** except the calculation of
    ``m`` from ``alphap`` and ``betap``, where in **R** ``m`` is defined
    with each type.

    References
    ----------
    .. [1] *R* statistical software: http://www.r-project.org/
    .. [2] *R* ``quantile`` function:
            http://stat.ethz.ch/R-manual/R-devel/library/stats/html/quantile.html

    Examples
    --------
    >>> from scipy.stats.mstats import mquantiles
    >>> a = np.array([6., 47., 49., 15., 42., 41., 7., 39., 43., 40., 36.])
    >>> mquantiles(a)
    array([ 19.2,  40. ,  42.8])

    Using a 2D array, specifying axis and limit.

    >>> data = np.array([[   6.,    7.,    1.],
    ...                  [  47.,   15.,    2.],
    ...                  [  49.,   36.,    3.],
    ...                  [  15.,   39.,    4.],
    ...                  [  42.,   40., -999.],
    ...                  [  41.,   41., -999.],
    ...                  [   7., -999., -999.],
    ...                  [  39., -999., -999.],
    ...                  [  43., -999., -999.],
    ...                  [  40., -999., -999.],
    ...                  [  36., -999., -999.]])
    >>> print(mquantiles(data, axis=0, limit=(0, 50)))
    [[ 19.2   14.6    1.45]
     [ 40.    37.5    2.5 ]
     [ 42.8   40.05   3.55]]

    >>> data[:, 2] = -999.
    >>> print(mquantiles(data, axis=0, limit=(0, 50)))
    [[19.200000000000003 14.6 --]
     [40.0 37.5 --]
     [42.800000000000004 40.05 --]]

    """
    def _quantiles1D(data,m,p):
        x = np.sort(data.compressed())
        n = len(x)
        if n == 0:
            return ma.array(np.empty(len(p), dtype=float), mask=True)
        elif n == 1:
            return ma.array(np.resize(x, p.shape), mask=nomask)
        aleph = (n*p + m)
        k = np.floor(aleph.clip(1, n-1)).astype(int)
        gamma = (aleph-k).clip(0,1)
        return (1.-gamma)*x[(k-1).tolist()] + gamma*x[k.tolist()]

    data = ma.array(a, copy=False)
    if data.ndim > 2:
        raise TypeError("Array should be 2D at most !")

    if limit:
        condition = (limit[0] < data) & (data < limit[1])
        data[~condition.filled(True)] = masked

    p = np.array(prob, copy=False, ndmin=1)
    m = alphap + p*(1.-alphap-betap)
    # Computes quantiles along axis (or globally)
    if (axis is None):
        return _quantiles1D(data, m, p)

    return ma.apply_along_axis(_quantiles1D, axis, data, m, p)


def scoreatpercentile(data, per, limit=(), alphap=.4, betap=.4):
    """Calculate the score at the given 'per' percentile of the
    sequence a.  For example, the score at per=50 is the median.

    This function is a shortcut to mquantile

    """
    if (per < 0) or (per > 100.):
        raise ValueError("The percentile should be between 0. and 100. !"
                         " (got %s)" % per)

    return mquantiles(data, prob=[per/100.], alphap=alphap, betap=betap,
                      limit=limit, axis=0).squeeze()


def plotting_positions(data, alpha=0.4, beta=0.4):
    """
    Returns plotting positions (or empirical percentile points) for the data.

    Plotting positions are defined as ``(i-alpha)/(n+1-alpha-beta)``, where:
        - i is the rank order statistics
        - n is the number of unmasked values along the given axis
        - `alpha` and `beta` are two parameters.

    Typical values for `alpha` and `beta` are:
        - (0,1)    : ``p(k) = k/n``, linear interpolation of cdf (R, type 4)
        - (.5,.5)  : ``p(k) = (k-1/2.)/n``, piecewise linear function
          (R, type 5)
        - (0,0)    : ``p(k) = k/(n+1)``, Weibull (R type 6)
        - (1,1)    : ``p(k) = (k-1)/(n-1)``, in this case,
          ``p(k) = mode[F(x[k])]``. That's R default (R type 7)
        - (1/3,1/3): ``p(k) = (k-1/3)/(n+1/3)``, then
          ``p(k) ~ median[F(x[k])]``.
          The resulting quantile estimates are approximately median-unbiased
          regardless of the distribution of x. (R type 8)
        - (3/8,3/8): ``p(k) = (k-3/8)/(n+1/4)``, Blom.
          The resulting quantile estimates are approximately unbiased
          if x is normally distributed (R type 9)
        - (.4,.4)  : approximately quantile unbiased (Cunnane)
        - (.35,.35): APL, used with PWM
        - (.3175, .3175): used in scipy.stats.probplot

    Parameters
    ----------
    data : array_like
        Input data, as a sequence or array of dimension at most 2.
    alpha : float, optional
        Plotting positions parameter. Default is 0.4.
    beta : float, optional
        Plotting positions parameter. Default is 0.4.

    Returns
    -------
    positions : MaskedArray
        The calculated plotting positions.

    """
    data = ma.array(data, copy=False).reshape(1,-1)
    n = data.count()
    plpos = np.empty(data.size, dtype=float)
    plpos[n:] = 0
    plpos[data.argsort()[:n]] = ((np.arange(1, n+1) - alpha) /
                                 (n + 1.0 - alpha - beta))
    return ma.array(plpos, mask=data._mask)

meppf = plotting_positions


def obrientransform(*args):
    """
    Computes a transform on input data (any number of columns).  Used to
    test for homogeneity of variance prior to running one-way stats.  Each
    array in ``*args`` is one level of a factor.  If an `f_oneway()` run on
    the transformed data and found significant, variances are unequal.   From
    Maxwell and Delaney, p.112.

    Returns: transformed data for use in an ANOVA
    """
    data = argstoarray(*args).T
    v = data.var(axis=0,ddof=1)
    m = data.mean(0)
    n = data.count(0).astype(float)
    # result = ((N-1.5)*N*(a-m)**2 - 0.5*v*(n-1))/((n-1)*(n-2))
    data -= m
    data **= 2
    data *= (n-1.5)*n
    data -= 0.5*v*(n-1)
    data /= (n-1.)*(n-2.)
    if not ma.allclose(v,data.mean(0)):
        raise ValueError("Lack of convergence in obrientransform.")

    return data


@np.deprecate(message="mstats.signaltonoise is deprecated in scipy 0.16.0")
def signaltonoise(data, axis=0):
    """Calculates the signal-to-noise ratio, as the ratio of the mean over
    standard deviation along the given axis.

    Parameters
    ----------
    data : sequence
        Input data
    axis : {0, int}, optional
        Axis along which to compute. If None, the computation is performed
        on a flat version of the array.
    """
    data = ma.array(data, copy=False)
    m = data.mean(axis)
    sd = data.std(axis, ddof=0)
    return m/sd


def sem(a, axis=0, ddof=1):
    """
    Calculates the standard error of the mean of the input array.

    Also sometimes called standard error of measurement.

    Parameters
    ----------
    a : array_like
        An array containing the values for which the standard error is
        returned.
    axis : int or None, optional
        If axis is None, ravel `a` first. If axis is an integer, this will be
        the axis over which to operate. Defaults to 0.
    ddof : int, optional
        Delta degrees-of-freedom. How many degrees of freedom to adjust
        for bias in limited samples relative to the population estimate
        of variance. Defaults to 1.

    Returns
    -------
    s : ndarray or float
        The standard error of the mean in the sample(s), along the input axis.

    Notes
    -----
    The default value for `ddof` changed in scipy 0.15.0 to be consistent with
    `stats.sem` as well as with the most common definition used (like in the R
    documentation).

    Examples
    --------
    Find standard error along the first axis:

    >>> from scipy import stats
    >>> a = np.arange(20).reshape(5,4)
    >>> print(stats.mstats.sem(a))
    [2.8284271247461903 2.8284271247461903 2.8284271247461903
     2.8284271247461903]

    Find standard error across the whole array, using n degrees of freedom:

    >>> print(stats.mstats.sem(a, axis=None, ddof=0))
    1.2893796958227628

    """
    a, axis = _chk_asarray(a, axis)
    n = a.count(axis=axis)
    s = a.std(axis=axis, ddof=ddof) / ma.sqrt(n)
    return s


F_onewayResult = namedtuple('F_onewayResult', ('statistic', 'pvalue'))


def f_oneway(*args):
    """
    Performs a 1-way ANOVA, returning an F-value and probability given
    any number of groups.  From Heiman, pp.394-7.

    Usage: ``f_oneway(*args)``, where ``*args`` is 2 or more arrays,
    one per treatment group.

    Returns
    -------
    statistic : float
        The computed F-value of the test.
    pvalue : float
        The associated p-value from the F-distribution.

    """
    # Construct a single array of arguments: each row is a group
    data = argstoarray(*args)
    ngroups = len(data)
    ntot = data.count()
    sstot = (data**2).sum() - (data.sum())**2/float(ntot)
    ssbg = (data.count(-1) * (data.mean(-1)-data.mean())**2).sum()
    sswg = sstot-ssbg
    dfbg = ngroups-1
    dfwg = ntot - ngroups
    msb = ssbg/float(dfbg)
    msw = sswg/float(dfwg)
    f = msb/msw
    prob = special.fdtrc(dfbg, dfwg, f)  # equivalent to stats.f.sf

    return F_onewayResult(f, prob)


@np.deprecate(message="mstats.f_value_wilks_lambda deprecated in scipy 0.17.0")
def f_value_wilks_lambda(ER, EF, dfnum, dfden, a, b):
    """Calculation of Wilks lambda F-statistic for multivariate data, per
    Maxwell & Delaney p.657.
    """
    ER = ma.array(ER, copy=False, ndmin=2)
    EF = ma.array(EF, copy=False, ndmin=2)
    if ma.getmask(ER).any() or ma.getmask(EF).any():
        raise NotImplementedError("Not implemented when the inputs "
                                  "have missing data")

    lmbda = np.linalg.det(EF) / np.linalg.det(ER)
    q = ma.sqrt(((a-1)**2*(b-1)**2 - 2) / ((a-1)**2 + (b-1)**2 - 5))
    q = ma.filled(q, 1)
    n_um = (1 - lmbda**(1.0/q))*(a-1)*(b-1)
    d_en = lmbda**(1.0/q) / (n_um*q - 0.5*(a-1)*(b-1) + 1)
    return n_um / d_en


FriedmanchisquareResult = namedtuple('FriedmanchisquareResult',
                                     ('statistic', 'pvalue'))


def friedmanchisquare(*args):
    """Friedman Chi-Square is a non-parametric, one-way within-subjects ANOVA.
    This function calculates the Friedman Chi-square test for repeated measures
    and returns the result, along with the associated probability value.

    Each input is considered a given group. Ideally, the number of treatments
    among each group should be equal. If this is not the case, only the first
    n treatments are taken into account, where n is the number of treatments
    of the smallest group.
    If a group has some missing values, the corresponding treatments are masked
    in the other groups.
    The test statistic is corrected for ties.

    Masked values in one group are propagated to the other groups.

    Returns
    -------
    statistic : float
        the test statistic.
    pvalue : float
        the associated p-value.

    """
    data = argstoarray(*args).astype(float)
    k = len(data)
    if k < 3:
        raise ValueError("Less than 3 groups (%i): " % k +
                         "the Friedman test is NOT appropriate.")

    ranked = ma.masked_values(rankdata(data, axis=0), 0)
    if ranked._mask is not nomask:
        ranked = ma.mask_cols(ranked)
        ranked = ranked.compressed().reshape(k,-1).view(ndarray)
    else:
        ranked = ranked._data
    (k,n) = ranked.shape
    # Ties correction
    repeats = np.array([find_repeats(_) for _ in ranked.T], dtype=object)
    ties = repeats[repeats.nonzero()].reshape(-1,2)[:,-1].astype(int)
    tie_correction = 1 - (ties**3-ties).sum()/float(n*(k**3-k))

    ssbg = np.sum((ranked.sum(-1) - n*(k+1)/2.)**2)
    chisq = ssbg * 12./(n*k*(k+1)) * 1./tie_correction

    return FriedmanchisquareResult(chisq,
                                   distributions.chi2.sf(chisq, k-1))
