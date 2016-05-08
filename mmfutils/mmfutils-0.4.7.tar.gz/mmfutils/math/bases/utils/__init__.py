"""General utility functions"""
from __future__ import absolute_import, division

__all__ = ('prod', 'norm', 'ndgrid', 'get_xs', 'get_ks', 'normalize',
           'fftn', 'ifftn', 'fftn', 'ifftn', 'resample',
           'dst', 'dct', 'idst', 'idct',
           'axpy', 'dotc',
           'zdscale', 'norm', 'scale',
           'get_coulomb_potential')

import collections
import copy
import functools
import itertools
import math
import operator
import types
import warnings

import numpy as np
from numpy.linalg import norm
import scipy as sp
from scipy.linalg import get_blas_funcs

import uncertainties.unumpy

from mmfutils.containers import Object
from mmfutils.performance.blas import zdotc, ddot, daxpy, zaxpy
from mmfutils.performance.fft import fft, ifft, fftn, ifftn, resample


def prod(x):
    """Equivalent of sum but with multiplication."""
    # http://stackoverflow.com/a/595396/1088938
    return functools.reduce(operator.mul, x, 1)


# Use the scipy BLAS routines for speed
def ndgrid(*v):
    """Sparse meshgrid with regular ordering."""
    if len(v) == 1:
        return v
    else:
        return np.meshgrid(*v, sparse=True, indexing='ij')


def zdscale(x, a, _zdscal=sp.linalg.blas.zdscal):
    x = x.ravel()
    assert x.flags.c_contiguous
    return _zdscal(a, x, overwrite_x=True)
    #assert res.base is x or res.base is x.base
    #return res


def scale(x, a):
    return get_blas_funcs(['scal'], [x])[0](a, x)


def get_xs(Ls, Ns):
    """Return `(x,y,z)` with broadcasting"""
    return ndgrid(*[_l/_n * np.arange(-_n/2, _n/2)
                    for _l, _n in zip(Ls, Ns)])


def get_ks(Ls, Ns):
    """Return list of ks in correct order for FFT."""
    return ndgrid(*[2*np.pi * np.fft.fftfreq(_n, _l/_n)
                    for _l, _n in zip(Ls, Ns)])


def normalize(phi, dV=1.0):
    """Return normalized phi with volume element dV"""
    phi /= norm(phi) * math.sqrt(dV)
    return phi


# Try to get the pyfftw routines, but fallback to numpy.fft if they cannot be
# imported.  The routines fftn and ifftn here transform the last three indices
# only, allowing use to use the full psis array.
if False:
    try:
        import pyfftw.interfaces.numpy_fft

        def fftn(x, axes=(-3, -2, -1),
                 _fftn=pyfftw.interfaces.numpy_fft.fftn):
            res = _fftn(x, axes=axes, threads=8)
            return res

        def ifftn(x, axes=(-3, -2, -1),
                  _ifftn=pyfftw.interfaces.numpy_fft.ifftn):
            res = _ifftn(x, axes=axes, threads=8)
            return res

        if pyfftw.version >= '0.9.2':
            pyfftw.interfaces.cache.enable()
            pyfftw.interfaces.cache.set_keepalive_time(60)

    except ImportError:
        warnings.warn("Could not import pyfftw. Using slower numpy.fft")

        def fftn(x, axes=(-3, -2, -1), _fftn=np.fft.fftn):
            res = _fftn(x, axes=axes)
            return res

        def ifftn(x, axes=(-3, -2, -1), _ifftn=np.fft.ifftn):
            res = _ifftn(x, axes=axes)
            return res

        fftn3 = fftn
        ifftn3 = ifftn


def get_coulomb_exact(y, Ls):
    """Return the convolution `int(C(x-r)*y(r),r)`"""
    Ls = np.asarray(Ls)
    dim = len(Ls)
    Ns = np.asarray(y.shape)
    D = np.sqrt((Ls**2).sum())  # Diameter of cell
    ds = Ls / Ns

    def C(k):
        return 4*np.pi*np.ma.divide(1 - np.cos(D*k), k**2).filled(D**2/2.0)

    y_padded = np.zeros(3*Ns, dtype=y.dtype)
    inds = [slice(0, _N) for _N in Ns]
    y_padded[inds] = y
    k = np.sqrt(sum(_K**2 for _K in get_ks(Ls=3*Ls, Ns=3*Ns)))
    return ifftn(C(k) * fftn(y_padded))[inds]


def get_coulomb_fast(y, Ls, correct=False):
    """Fast version of the Coulomb potential on small lattice"""
    Ls = np.asarray(Ls)
    dim = len(Ls)
    Ns = np.asarray(y.shape)
    N0 = Ns//3
    y0 = resample(y, N0)
    V = resample(get_coulomb_exact(y0, Ls=Ls), Ns)
    if correct:
        k = np.sqrt(sum(_K**2 for _K in get_ks(Ls=Ls, Ns=Ns)))
        C = 4*np.pi*np.ma.divide(1.0, k**2).filled(0.0)
        V += ifftn(C * fftn(y - resample(y0, N)))
    return V


def get_coulomb_potential(rho, Ls):
    """Return the Hartree portion of the Coulomb potential (no e2 factor)."""
    return get_coulomb_fast(rho, Ls=Ls)


class Covariance(Object, collections.Sequence):
    """Represents a set of parameters with error estimates and covariance.

    >>> c = Covariance([1, 2, 3], [[1, 0, 0], [0, 4, 0], [0, 0, 0.25]],
    ...                tags=['a', 'b', 'c'])
    >>> c
    Covariance(covariance_matrix=array([[ 1. ,  0. ,  0. ],
           [ 0. ,  4. ,  0. ],
           [ 0. ,  0. ,  0.25]]), ... tags=['a', 'b', 'c'], x=array([1, 2, 3]))
    >>> print c
    a = 1.0(1.0), b = 2.0(2.0), c = 3.00(50)
    """
    def __init__(self, x, covariance_matrix=None, tags=None,
                 precision=2, sep=', '):
        self.__dict__['x'] = np.asarray(x)
        if covariance_matrix is not None:
            covariance_matrix = np.asarray(covariance_matrix)
        self.__dict__['covariance_matrix'] = covariance_matrix
        self.tags = tags
        self.precision = precision
        self.sep = sep
        Object.__init__(self)

    def init(self):
        self.u = self.compute_u()

    @property
    def covariance_matrix(self):
        return self.__dict__['covariance_matrix']

    @property
    def x(self):
        return self.__dict__['x']

    def compute_u(self):
        """Return the uncertainties"""
        return uncertainties.correlated_values(
            nom_values=self.x, covariance_mat=self.covariance_matrix,
            tags=self.tags)

    # Methods for the Sequence ABC
    def __len__(self):
        return len(self.tags)

    def __getitem__(self, key):
        if isinstance(key, types.StringType):
            key = self.tags.index(key)
        return self.u[key]

    @property
    def n(self):
        return uncertainties.unumpy.nominal_values(self.u)

    @property
    def s(self):
        return uncertainties.unumpy.std_devs(self.u)

    @property
    def correlation_matrix(self):
        return uncertainties.correlation_matrix(self.u)

    @property
    def correlated_values(self):
        return self.u

    def __str__(self):
        if self.tags:
            vals = map("{{0[0]}} = {{0[1]:.{}uS}}"
                       .format(self.precision).format, zip(self.tags, self.u))
        else:
            vals = map("{{:.{}uS}}".format(self.precision).format, self.u)

        return self.sep.join(vals)

    def get_PCA(self, check=True):
        """Return the uncorrelated principle components."""
        C = self.covariance_matrix
        if check:
            assert np.allclose(C, C.T)
        else:
            C = (C + C.T)/2.0
        d, V = np.linalg.eigh(C)

        # Make largest components positive
        V *= np.sign(V[np.argmax(abs(V), axis=0),
                       xrange(len(V))])[None, :]
        if check:
            assert np.allclose(V.T.dot(V), np.eye(len(d)))
            assert np.allclose(C.dot(V), V.dot(np.diag(d)))
            assert np.allclose(V.dot(d[:, None]*V.T), C)

        c = V.T.dot(self.as_list())
        x = uncertainties.unumpy.nominal_values(c)
        dx = uncertainties.unumpy.std_devs(c)
        # This sorts by relative error
        inds = np.argsort(abs(dx)/np.maximum(abs(dx), abs(x)))
        # This sorts by absolute error
        inds = np.argsort(abs(dx))

        tags = np.array(map('p_{}'.format, xrange(len(d))))
        return covariance(zip(tags, c[inds]), self.__class__), V[:, inds]

    def plot_correlations(self, cmap=None):
        from matplotlib import pyplot as plt
        from matplotlib.colors import LinearSegmentedColormap

        if cmap is None:
            # Nice divergent colormap with black for zero
            cmap = LinearSegmentedColormap(
                name='brdiverge',
                segmentdata=dict(
                    red=[(0.0, 0.0, 0.0),
                         (0.5, 0.0, 0.0),
                         (1.0, 1.0, 1.0)],
                    green=[(0.0, 1.0, 1.0),
                           (0.5, 0.0, 0.0),
                           (1.0, 0.0, 0.0)],
                    blue=[(0.0, 1.0, 1.0),
                          (0.5, 0.0, 0.0),
                          (1.0, 1.0, 1.0)]))
        imgplot = plt.imshow(
            self.correlation_matrix, vmin=-1, vmax=1, cmap=cmap,
            interpolation='none', origin=0)
        plt.colorbar()
        if self.tags:
            plt.xticks(*zip(*enumerate(self.tags)))
            plt.yticks(*zip(*enumerate(self.tags)))
        return imgplot

    def plot_PCA(self, **kw):
        """Plot the PCA eigenvectors"""
        import sympy
        from matplotlib import pyplot as plt
        pca, V = self.get_PCA(**kw)
        x = np.arange(len(pca.tags))

        def format_tag(tag, value=None):
            ftag = sympy.latex(sympy.S(tag))
            if value is None:
                return r"${}$".format(ftag)
            else:
                return r"${} = {}$".format(ftag, value)

        fig, axs = plt.subplots(len(pca.tags), 1)
        for n, tag in enumerate(pca.tags):
            ax = axs[n]
            ax.bar(x, V[:, n], width=1.0, color='k')
            ax.set_ylim(-1, 1)
            ax.set_axis_bgcolor((1.0, 1.0, 0.9))

            # remove all the axes
            for k, v in ax.spines.items():
                v.set_visible(False)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.yaxis.set_label_position("right")
            ax.set_ylabel(format_tag(tag, r"{:0.2uS}".format(pca[n])),
                          rotation='horizontal', ha='left')

        ax.set_xticks(x+0.5)
        ax.xaxis.set_ticklabels(map(format_tag, self.tags))
        return fig

    def as_dict(self):
        d = copy.copy(self)
        d.__class__ = CovarianceDict
        return d

    def as_list(self):
        d = copy.copy(self)
        d.__class__ = Covariance
        return d


class CovarianceDict(Covariance, collections.Mapping):
    """Covariance class that acts like a dict rather than a tuple."""
    def __iter__(self):
        for _x in self.tags:
            yield _x


def covariance(value_dict, Cls=Covariance):
    """Return a Covariance object from a dictionary of ufloats"""
    value_dict = collections.OrderedDict(value_dict)
    tags = value_dict.keys()
    covariance_matrix = uncertainties.covariance_matrix(value_dict.values())
    x = map(uncertainties.nominal_value, value_dict.values())
    return Cls(x=x, covariance_matrix=covariance_matrix, tags=tags)


######################################################################
# 1D FFTs for real functions.
def dst(f):
    """Return the Discrete Sine Transform (DST III) of `f`"""
    return sp.fftpack.dst(f, type=3, axis=-1)


def idst(F):
    """Return the Inverse Discrete Sine Transform (DST II) of `f`"""
    N = F.shape[-1]
    return sp.fftpack.dst(F, type=2, axis=-1)/(2.0*N)


def dct(f):
    """Return the Discrete Sine Transform (DST III) of `f`"""
    return sp.fftpack.dct(f, type=2, axis=-1)


def idct(F):
    """Return the Inverse Discrete Sine Transform (DST II) of `f`"""
    N = F.shape[-1]
    return sp.fftpack.dct(F, type=2, axis=-1)/(2.0*N)


######################################################################
# BLAS wrappers
def axpy(y, x, a):
    if np.iscomplexobj(y) or np.iscomplexobj(x) or np.iscomplexobj(a):
        return zaxpy(y=y, x=x, a=a)
    else:
        return daxpy(y=y, x=x, a=a)


def dotc(a, b):
    if np.iscomplexobj(a) or np.iscomplexobj(b):
        return zdotc(a, b)
    else:
        return ddot(a, b)
