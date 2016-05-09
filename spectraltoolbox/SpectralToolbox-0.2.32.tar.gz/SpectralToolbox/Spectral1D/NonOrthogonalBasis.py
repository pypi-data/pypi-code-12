# -*- coding: utf-8 -*-

#
# This file is part of SpectralToolbox.
#
# SpectralToolbox is free software: you can redistribute it and/or modify
# it under the terms of the LGNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SpectralToolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LGNU Lesser General Public License for more details.
#
# You should have received a copy of the LGNU Lesser General Public License
# along with SpectralToolbox.  If not, see <http://www.gnu.org/licenses/>.
#
# DTU UQ Library
# Copyright (C) 2012-2015 The Technical University of Denmark
# Scientific Computing Section
# Department of Applied Mathematics and Computer Science
#
# Copyright (C) 2015-2016 Massachusetts Institute of Technology
# Uncertainty Quantification group
# Department of Aeronautics and Astronautics
#
# Author: Daniele Bigoni
#

import numpy as np

from SpectralToolbox.Spectral1D.Constants import *
from SpectralToolbox.Spectral1D.AbstractClasses import *
from SpectralToolbox.Spectral1D.OrthogonalFunctions import *
from SpectralToolbox.Spectral1D.OrthogonalPolynomials import *

__all__ = ['ConstantExtendedHermiteProbabilistsFunction',
           'HermiteProbabilistsRadialBasisFunction',
           'ConstantExtendedHermiteProbabilistsRadialBasisFunction',
           'LinearExtendedHermiteProbabilistsRadialBasisFunction']

class ConstantExtendedHermiteProbabilistsFunction(Basis):
    r""" Construction of the Hermite Probabilists' functions extended with the constant basis

    The basis is defined by:

    .. math::

       \phi_0(x) = 1 \qquad \phi_i(x) = \psi_{i-1}(x) \quad \text{for } i=1\ldots

    where :math:`\psi_j` are the Hermite Probabilists' functions.

    Args:
      normalized (bool): whether to normalize the underlying polynomials.
        Default=``None`` which leaves the choice at evaluation time.
    """
    def __init__(self, normalized=None):
        self.hpf = HermiteProbabilistsFunction(normalized)

    def Quadrature(self, N, quadType=None, norm=False):
        r""" Generate quadrature rules of the selected type.

        .. seealso:: :func:`OrthogonalPolynomial.Quadrature`
        """
        if quadType in [None, GAUSS]:
            return self.GaussQuadrature(N, norm)
        else:
            raise ValueError("quadType=%s not available" % quadType)

    def GaussQuadrature(self, N, norm=False):
        r""" Hermite Probabilists' function Gauss quadratures

        .. seealso:: :func:`OrthogonalPolynomial.GaussQuadrature`
        """
        return self.hpf.GaussQuadrature(N, norm)

    def Evaluate(self, x, N, norm=True):
        r""" Evaluate the ``N``-th order constant extended Hermite Probabilists' function

        .. seealso:: :func:`OrthogonalPolynomial.Evaluate`
        """
        if N > 0:
            p = self.hpf.Evaluate(x, N-1, norm)
        else:
            p = np.ones(x.shape[0])
        return p

    def GradEvaluate(self, x, N, k=0, norm=True):
        r""" Evaluate the ``k``-th derivative of the ``N``-th order constant extended Hermite Probabilists' function

        .. seealso:: :func:`HermitePhysicistsFunction.GradEvaluate`
        """
        if N > 0:
            dp = self.hpf.GradEvaluate(x, N-1, k, norm)
        else:
            dp = np.ones(x.shape[0]) if k == 0 else np.zeros(x.shape[0])
        return dp

    def GradVandermonde(self, r, N, k=0, norm=True):
        r""" Generate the ``k``-th derivative of the ``N``-th order Vandermoned matrix.

        Args:
          r (:class:`ndarray<ndarray>` [``m``]): set of ``m`` points where to
            evaluate the polynomials
          N (int): maximum polynomial order
          k (int): order of the derivative
          norm (bool): whether to return normalized (``True``) or unnormalized
            (``False``) polynomial. The parameter is ignored if the ``normalized``
            parameter is provided at construction time.

        Returns:
          (:class:`ndarray<ndarray>` [``m``,``N+1``]) -- polynomials evaluated
            at the ``r`` points.
        """
        DVr = np.zeros((r.shape[0],N+1))
        for i in range(0,N+1):
            DVr[:,i] = self.GradEvaluate(r, i, k, norm)
        return DVr

class HermiteProbabilistsRadialBasisFunction(Basis):
    r""" Construction of the Hermite Probabilists' Radial Basis Functions

    For the set :math:`\left\{x_i\right\}_{i=1}^N` of Gauss-Hermite points,
    the basis are defined by:

    .. math::

       \phi_i(x) = \begin{cases}
       \exp\left( -\frac{(x-x_i)^2}{2\sigma^2_{i-1}} \right) & \text{if } x \leq x_i
       \exp\left( -\frac{(x-x_i)^2}{2\sigma^2_{i}} \right) & \text{if } x > x_i
       \end{cases}

    where :math:`\sigma_i=x_{i+1} - x_{i}`, :math:`\sigma_0=\sigma_1` and
    :math:`\sigma_N=\sigma_{N-1}`

    Args:
      nknots (int): number of knots points :math:`x_i`
      scale (float): scaling for the badwidth :math:`\sigma`.
    """

    def __init__(self, nknots, scale=1.):
        if nknots < 1:
            raise ValueError("Range error. nknots >= 1 must hold")
        self.nknots = nknots
        self.hp = HermiteProbabilistsPolynomial()
        self.xknots, self.wknots = self.hp.GaussQuadrature(self.nknots-1)
        self.sigma = np.zeros(self.nknots+1)
        if self.nknots == 1:
            self.sigma[:] = 1.
        else:
            self.sigma[1:-1] = np.diff(self.xknots)
            self.sigma[0] = self.sigma[1]
            self.sigma[-1] = self.sigma[-2]
        self.sigma *= scale

    def Quadrature(self, N, quadType=None, norm=False):
        r""" Generate quadrature rules of the selected type.

        .. seealso:: :func:`OrthogonalPolynomial.Quadrature`
        """
        if quadType in [None, GAUSS]:
            return self.GaussQuadrature(N, norm)
        else:
            raise ValueError("quadType=%s not available" % quadType)

    def GaussQuadrature(self, N, norm=False):
        r""" Hermite Probabilists' function Gauss quadratures

        .. seealso:: :func:`OrthogonalPolynomial.GaussQuadrature`
        """
        return self.hp.GaussQuadrature(N, norm)

    def Evaluate(self, x, N, norm=True, extended_output=False):
        r""" Evaluate the ``N``-th Hermite Probabilists' Radial Basis Function

        .. seealso:: :func:`OrthogonalPolynomial.Evaluate`
        """
        if N > self.nknots:
            raise ValueError("N must be <= than the number of knots")
        leq = (x <= self.xknots[N])
        left = np.where(leq)[0]
        right = np.where(np.logical_not(leq))[0]
        out = np.zeros(x.shape[0])
        diff = x - self.xknots[N]
        out[left] = np.exp( - (diff[left])**2./(2.*self.sigma[N-1]**2.) )
        out[right] = np.exp( - (diff[right])**2./(2.*self.sigma[N]**2.) )
        if extended_output:
            return (out, left, right, diff)
        else:
            return out

    def GradEvaluate(self, x, N, k=0, norm=True):
        r""" Evaluate the ``k``-th derivative of the ``N``-th Hermite Probabilists' Radial Basis Function

        .. seealso:: :func:`OrthogonalPolynomial.GradEvaluate`
        """
        (out, left, right, diff) = self.Evaluate(x, N, norm, extended_output=True)
        if k == 0:
            return out
        elif k == 1:
            out[left] *= -diff[left]/self.sigma[N-1]**2.
            out[right] *= -diff[right]/self.sigma[N]**2.
        elif k == 2:
            out[left] *= ( -1./self.sigma[N-1]**2. + diff[left]**2./self.sigma[N-1]**4. )
            out[right] *= ( -1./self.sigma[N]**2. + diff[right]**2./self.sigma[N]**4. )
        elif k == 3:
            out[left] *= diff[left] * (3.*self.sigma[N-1]**2. - diff[left]**2.) / self.sigma[N-1]**6.
            out[right] *= diff[right] * (3.*self.sigma[N]**2. - diff[right]**2.) / self.sigma[N]**6.
        else:
            raise ValueError("%d-th derivative not defined yet" % k)
        return out

    def GradVandermonde(self, r, N, k=0, norm=True):
        r""" Generate the ``k``-th derivative of the ``N``-th order Vandermoned matrix.

        Args:
          r (:class:`ndarray<ndarray>` [``m``]): set of ``m`` points where to
            evaluate the polynomials
          N (int): maximum polynomial order
          k (int): order of the derivative
          norm (bool): whether to return normalized (``True``) or unnormalized
            (``False``) polynomial. The parameter is ignored if the ``normalized``
            parameter is provided at construction time.

        Returns:
          (:class:`ndarray<ndarray>` [``m``,``N+1``]) -- polynomials evaluated
            at the ``r`` points.
        """
        DVr = np.zeros((r.shape[0],N+1))
        for i in range(0,N+1):
            DVr[:,i] = self.GradEvaluate(r, i, k, norm)
        return DVr

class ConstantExtendedHermiteProbabilistsRadialBasisFunction(Basis):
    r""" Construction of the Hermite Probabilists' Radial Basis Functions

    For the set :math:`\left\{x_i\right\}_{i=1}^N` of Gauss-Hermite points,
    the basis :math:`\{\phi_i\}_{i=0}^M` are defined by:

    .. math::

       \phi_0(x) = 1 \\
       \phi_i(x) = \begin{cases}
       \exp\left( -\frac{(x-x_i)^2}{2\sigma^2_{i-1}} \right) & \text{if } x \leq x_i
       \exp\left( -\frac{(x-x_i)^2}{2\sigma^2_{i}} \right) & \text{if } x > x_i
       \end{cases}

    where :math:`\sigma_i=x_{i+1} - x_{i}`, :math:`\sigma_0=\sigma_1` and
    :math:`\sigma_N=\sigma_{N-1}`

    Args:
      order (int): maximum order :math:`M`
      scale (float): scaling for the badwidth :math:`\sigma`.
    """

    def __init__(self, nbasis, scale=1.):
        self.nbasis = nbasis
        self.nknots = nbasis - 1
        self.hp = HermiteProbabilistsPolynomial()
        self.xknots, self.wknots = self.hp.GaussQuadrature(self.nknots-1)
        self.sigma = np.zeros(self.nknots+1)
        if self.nknots == 1:
            self.sigma[:] = 1.
        else:
            self.sigma[1:-1] = np.diff(self.xknots)
            self.sigma[0] = self.sigma[1]
            self.sigma[-1] = self.sigma[-2]
        self.sigma *= scale

    def Quadrature(self, N, quadType=None, norm=False):
        r""" Generate quadrature rules of the selected type.

        .. seealso:: :func:`OrthogonalPolynomial.Quadrature`
        """
        if quadType in [None, GAUSS]:
            return self.GaussQuadrature(N, norm)
        else:
            raise ValueError("quadType=%s not available" % quadType)

    def GaussQuadrature(self, N, norm=False):
        r""" Hermite Probabilists' function Gauss quadratures

        .. seealso:: :func:`OrthogonalPolynomial.GaussQuadrature`
        """
        return self.hp.GaussQuadrature(N, norm)

    def Evaluate(self, x, N, norm=True, extended_output=False):
        r""" Evaluate the ``N``-th Hermite Probabilists' Radial Basis Function

        .. seealso:: :func:`OrthogonalPolynomial.Evaluate`
        """
        if N > self.nbasis:
            raise ValueError("N must be <= than the number of basis")
        if N == 0:
            out = np.ones(x.shape[0])
            left = None
            right = None
            diff = None
        else:
            nrbf = N-1
            leq = (x <= self.xknots[nrbf])
            left = np.where(leq)[0]
            right = np.where(np.logical_not(leq))[0]
            out = np.zeros(x.shape[0])
            diff = x - self.xknots[nrbf]
            out[left] = np.exp( - (diff[left])**2./(2.*self.sigma[nrbf-1]**2.) )
            out[right] = np.exp( - (diff[right])**2./(2.*self.sigma[nrbf]**2.) )
        if extended_output:
            return (out, left, right, diff)
        else:
            return out

    def GradEvaluate(self, x, N, k=0, norm=True):
        r""" Evaluate the ``k``-th derivative of the ``N``-th Hermite Probabilists' Radial Basis Function

        .. seealso:: :func:`OrthogonalPolynomial.GradEvaluate`
        """
        if N == 0 and k > 0:
            return np.zeros(x.shape[0])
        (out, left, right, diff) = self.Evaluate(x, N, norm, extended_output=True)
        nrbf = N-1
        if k == 0:
            return out
        elif k == 1:
            out[left] *= -diff[left]/self.sigma[nrbf-1]**2.
            out[right] *= -diff[right]/self.sigma[nrbf]**2.
        elif k == 2:
            out[left] *= ( -1./self.sigma[nrbf-1]**2. + diff[left]**2./self.sigma[nrbf-1]**4. )
            out[right] *= ( -1./self.sigma[nrbf]**2. + diff[right]**2./self.sigma[nrbf]**4. )
        elif k == 3:
            out[left] *= diff[left] * (3.*self.sigma[nrbf-1]**2. - diff[left]**2.) / \
                         self.sigma[nrbf-1]**6.
            out[right] *= diff[right] * (3.*self.sigma[nrbf]**2. - diff[right]**2.) / \
                          self.sigma[nrbf]**6.
        else:
            raise ValueError("%d-th derivative not defined yet" % k)
        return out

    def GradVandermonde(self, r, N, k=0, norm=True):
        r""" Generate the ``k``-th derivative of the ``N``-th order Vandermoned matrix.

        Args:
          r (:class:`ndarray<ndarray>` [``m``]): set of ``m`` points where to
            evaluate the polynomials
          N (int): maximum polynomial order
          k (int): order of the derivative
          norm (bool): whether to return normalized (``True``) or unnormalized
            (``False``) polynomial. The parameter is ignored if the ``normalized``
            parameter is provided at construction time.

        Returns:
          (:class:`ndarray<ndarray>` [``m``,``N+1``]) -- polynomials evaluated
            at the ``r`` points.
        """
        DVr = np.zeros((r.shape[0],N+1))
        for i in range(0,N+1):
            DVr[:,i] = self.GradEvaluate(r, i, k, norm)
        return DVr

class LinearExtendedHermiteProbabilistsRadialBasisFunction(Basis):
    r""" Construction of the Hermite Probabilists' Radial Basis Functions

    For the set :math:`\left\{x_i\right\}_{i=1}^N` of Gauss-Hermite points,
    the basis :math:`\{\phi_i\}_{i=0}^M` are defined by:

    .. math::

       \phi_0(x) = 1 \\
       \phi_1(x) = x \\
       \phi_i(x) = \begin{cases}
       \exp\left( -\frac{(x-x_i)^2}{2\sigma^2_{i-1}} \right) & \text{if } x \leq x_i
       \exp\left( -\frac{(x-x_i)^2}{2\sigma^2_{i}} \right) & \text{if } x > x_i
       \end{cases}

    where :math:`\sigma_i=x_{i+1} - x_{i}`, :math:`\sigma_0=\sigma_1` and
    :math:`\sigma_N=\sigma_{N-1}`

    Args:
      order (int): maximum order :math:`M`
      scale (float): scaling for the badwidth :math:`\sigma`.
    """

    def __init__(self, nbasis, scale=1.):
        self.nbasis = nbasis
        self.nknots = nbasis - 2
        self.hp = HermiteProbabilistsPolynomial()
        self.xknots, self.wknots = self.hp.GaussQuadrature(self.nknots-1)
        self.sigma = np.zeros(self.nknots+1)
        if self.nknots == 1:
            self.sigma[:] = 1.
        else:
            self.sigma[1:-1] = np.diff(self.xknots)
            self.sigma[0] = self.sigma[1]
            self.sigma[-1] = self.sigma[-2]
        self.sigma *= scale

    def Quadrature(self, N, quadType=None, norm=False):
        r""" Generate quadrature rules of the selected type.

        .. seealso:: :func:`OrthogonalPolynomial.Quadrature`
        """
        if quadType in [None, GAUSS]:
            return self.GaussQuadrature(N, norm)
        else:
            raise ValueError("quadType=%s not available" % quadType)

    def GaussQuadrature(self, N, norm=False):
        r""" Hermite Probabilists' function Gauss quadratures

        .. seealso:: :func:`OrthogonalPolynomial.GaussQuadrature`
        """
        return self.hp.GaussQuadrature(N, norm)

    def Evaluate(self, x, N, norm=True, extended_output=False):
        r""" Evaluate the ``N``-th Hermite Probabilists' Radial Basis Function

        .. seealso:: :func:`OrthogonalPolynomial.Evaluate`
        """
        if N > self.nbasis:
            raise ValueError("N must be <= than the number of basis")
        if N == 0:
            out = np.ones(x.shape[0])
            left = None
            right = None
            diff = None
        elif N == 1:
            out = x.flatten()
            left = None
            right = None
            diff = None
        else:
            nrbf = N-2
            leq = (x <= self.xknots[nrbf])
            left = np.where(leq)[0]
            right = np.where(np.logical_not(leq))[0]
            out = np.zeros(x.shape[0])
            diff = x - self.xknots[nrbf]
            out[left] = np.exp( - (diff[left])**2./(2.*self.sigma[nrbf-1]**2.) )
            out[right] = np.exp( - (diff[right])**2./(2.*self.sigma[nrbf]**2.) )
        if extended_output:
            return (out, left, right, diff)
        else:
            return out

    def GradEvaluate(self, x, N, k=0, norm=True):
        r""" Evaluate the ``k``-th derivative of the ``N``-th Hermite Probabilists' Radial Basis Function

        .. seealso:: :func:`OrthogonalPolynomial.GradEvaluate`
        """
        if N == 0 and k > 0:
            return np.zeros(x.shape[0])
        if N == 1:
            if k == 1:
                return np.ones(x.shape[0])
            elif k > 1:
                return np.zeros(x.shape[0])
        (out, left, right, diff) = self.Evaluate(x, N, norm, extended_output=True)
        nrbf = N-2
        if k == 0:
            return out
        elif k == 1:
            out[left] *= -diff[left]/self.sigma[nrbf-1]**2.
            out[right] *= -diff[right]/self.sigma[nrbf]**2.
        elif k == 2:
            out[left] *= ( -1./self.sigma[nrbf-1]**2. + diff[left]**2./self.sigma[nrbf-1]**4. )
            out[right] *= ( -1./self.sigma[nrbf]**2. + diff[right]**2./self.sigma[nrbf]**4. )
        elif k == 3:
            out[left] *= diff[left] * (3.*self.sigma[nrbf-1]**2. - diff[left]**2.) / \
                         self.sigma[nrbf-1]**6.
            out[right] *= diff[right] * (3.*self.sigma[nrbf]**2. - diff[right]**2.) / \
                          self.sigma[nrbf]**6.
        else:
            raise ValueError("%d-th derivative not defined yet" % k)
        return out

    def GradVandermonde(self, r, N, k=0, norm=True):
        r""" Generate the ``k``-th derivative of the ``N``-th order Vandermoned matrix.

        Args:
          r (:class:`ndarray<ndarray>` [``m``]): set of ``m`` points where to
            evaluate the polynomials
          N (int): maximum polynomial order
          k (int): order of the derivative
          norm (bool): whether to return normalized (``True``) or unnormalized
            (``False``) polynomial. The parameter is ignored if the ``normalized``
            parameter is provided at construction time.

        Returns:
          (:class:`ndarray<ndarray>` [``m``,``N+1``]) -- polynomials evaluated
            at the ``r`` points.
        """
        DVr = np.zeros((r.shape[0],N+1))
        for i in range(0,N+1):
            DVr[:,i] = self.GradEvaluate(r, i, k, norm)
        return DVr