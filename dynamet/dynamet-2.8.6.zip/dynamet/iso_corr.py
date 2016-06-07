# -*- coding: utf-8 -*-
"""
Created on Mon Jun 01 16:36:43 2015

@author: pkiefer
"""

from scipy.optimize import nnls
import numpy as np
import math
import emzed

def lfac(n):
    return math.lgamma(n+1)

def lbinom(n, m):
    return lfac(n) - lfac(m) - lfac(n - m)

def pc(m, l, n, p13):
    """
    p(n_13 = m | n_l = l) for n C-atoms and natural abundance p13 of C13
    """
    if l > m:
        return 0.0
    f1 = lbinom(n - l, m - l)
    f2 = math.log(1.0 - p13) * (n - m)
    f3 = math.log(p13) * (m - l)
    return math.exp(f1 + f2 + f3)


def generate_matrix(n):
    p13 = emzed.abundance.C13
    mat = np.zeros((n+1, n+1))
    for i in range(n + 1):
        for j in range(n + 1):
            mat[i, j] = pc(i, j, n, p13)
    return mat


def bin_dist(n, p):
    rv = np.zeros((n + 1,))
    for i in range(n + 1):
        rv[i] = math.exp(lbinom(n, i)) * p ** i * (1.0 - p) ** (n - i)
    return rv


def compute_distribution_of_labeling(intensities, n):
#    intensities += [0] * (n + 1 - len(intensities))
    intensities = np.array(intensities)
    intensities /= np.sum(intensities)
    mat = generate_matrix(n)
    # modify matrix and rhs for constraint that solution vec sums up to 1.0:
    mat_modified = mat[:, 1:] - mat[:, :1]
    rhs_modified = intensities - mat[:, 0]
    corrected, error = nnls(mat_modified, rhs_modified)
    corrected = np.hstack((1.0 - np.sum(corrected), corrected))
    return corrected, error


#for n in range(2, 25):
#    t = emzed.utils.isotopeDistributionTable("C%d" % n, minp=1e-8)
#    t = t.filter(t.mf.isNotNone())
#    values = list(compute_distribution_of_labeling(list(t.abundance * 100), n)[0])[:10]
#    print "%3d" % n, " ".join(["%.6f" % v for v in values])


