"""
Provides the base class for all quadrature rules.
"""

import numpy as np
import copy

class QuadRule(object):
    """
    Provides an abstract base class for all quadrature rules.

    Parameters
    ----------

    order : int
        The polynomial order up to which the quadrature should be exact
    """

    def __init__(self, order, dimension):
        self._order = order
        self._dimension = dimension
        self._points = [None] * (dimension + 1)
        self._weights = [None] * (dimension + 1)

        self._set_data()

    def _set_data(self):
        """
        Sets the quadrature points and weights.
        """
        raise NotImplementedError()

    @property
    def order(self):
        return self._order

    @property
    def dimension(self):
        return self._dimension
    
    @property
    def points(self):
        return copy.deepcopy(self._points)

    @property
    def weights(self):
        return copy.deepcopy(self._weights)
