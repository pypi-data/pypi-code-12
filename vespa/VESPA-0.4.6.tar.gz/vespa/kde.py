
from __future__ import division, print_function, absolute_import

from scipy.stats import gaussian_kde as scipy_kde
import numpy as np
import math

from numba import jit

@jit(nopython=True)
def mul(A, x):
    """
    multiplying a matrix by a row vector
    """
    m,n = A.shape #rows, cols
    res = np.zeros(m, dtype=np.float64)

    for i in range(m):
        for j in range(n):
            res[i] += A[i,j]*x[j]

    return res

@jit(nopython=True)
def evaluate_kde(dataset, points, inv_cov, norm_factor):
    """
    Optimized evaluate

    Parameters
    ----------
    points : (# of dimensions, # of points)-array

    """
    d, n = dataset.shape
    d, m = points.shape

    result = np.zeros(m, dtype=np.float64)
    diff = np.empty(d, dtype=np.float64)

    #looping over points
    for i in range(m):
        for j in range(n):
            for k in range(d):
                diff[k] = dataset[k,j] - points[k,i]
            tdiff = mul(inv_cov, diff)
            for k in range(d):
                result[i] += math.exp(-diff[k]*tdiff[k] / 2.) / norm_factor

    return result

class gaussian_kde(scipy_kde):

    def evaluate_new(self, points):
        return evaluate_kde(self.dataset, np.atleast_2d(points),
                            self.inv_cov, self._norm_factor)
        
    def evaluate(self, points):
        """Evaluate the estimated pdf on a set of points.

        Parameters
        ----------
        points : (# of dimensions, # of points)-array
            Alternatively, a (# of dimensions,) vector can be passed in and
            treated as a single point.

        Returns
        -------
        values : (# of points,)-array
            The values at each point.

        Raises
        ------
        ValueError : if the dimensionality of the input points is different than
                     the dimensionality of the KDE.

        """
        points = np.atleast_2d(points)

        d, m = points.shape
        if d != self.d:
            if d == 1 and m == self.d:
                # points was passed in as a row vector
                points = np.reshape(points, (self.d, 1))
                m = 1
            else:
                msg = "points have dimension %s, dataset has dimension %s" % (d,
                    self.d)
                raise ValueError(msg)

        result = np.zeros((m,), dtype=float)

        if m >= self.n:
            # there are more points than data, so loop over data
            for i in range(self.n):
                diff = self.dataset[:, i, np.newaxis] - points
                tdiff = np.dot(self.inv_cov, diff)
                energy = np.sum(diff*tdiff,axis=0) / 2.0
                result = result + np.exp(-energy)
        else:
            # loop over points
            for i in range(m):
                diff = self.dataset - points[:, i, np.newaxis]
                tdiff = np.dot(self.inv_cov, diff)
                energy = np.sum(diff * tdiff, axis=0) / 2.0
                result[i] = np.sum(np.exp(-energy), axis=0)

        result = result / self._norm_factor

        return result

    __call__ = evaluate

