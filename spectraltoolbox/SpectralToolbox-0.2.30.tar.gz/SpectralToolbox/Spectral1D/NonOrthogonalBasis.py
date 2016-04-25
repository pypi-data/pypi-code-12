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

from SpectralToolbox.Spectral1D.AbstractClasses import *
from SpectralToolbox.Spectral1D.OrthogonalFunctions import *

__all__ = ['ConstantExtendedHermiteProbabilistsFunction']

class ConstantExtendedHermiteProbabilistsFunction(Basis):
    r""" Construction of the Hermite Probabilists' functions extended with the constant basis

    The basis is defined by:

    .. math::

       \phi_0(x) = 1 \qquad \phi_i(x) = \psi_{i-1}(x) \quad \text{for } i=1\ldots

    where :math:`\psi_j` are the Hermite Probabilists' functions.
    """
    def __init__(self):
        self.hpf = HermiteProbabilistsFunction()

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
                