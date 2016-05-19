"""
Provides the base class for all finite element classes.
"""

# IMPORTS
import numpy as np

class Element(object):
    """
    Provides an abstract base class for all reference elements.

    Derived classes have to implement the methods

    * :py:meth:`_eval_d0_basis(points)`
    * :py:meth:`_eval_d1_basis(points)`
    * :py:meth:`_eval_d2_basis(points)`

    that evaluate the basis functions or their derivatives.

    Parameters
    ----------

    dimension : int
        The spatial dimension of the element

    order : int
        The polynomial order of the basis functions

    n_basis : iterable
        The number of basis functions related to the entities of
        every topological dimension

    n_verts : iterable
        The number of vertices for the entities of
        each topological dimension
    """

    is_nodal = False
    is_hierarchic = False

    def __init__(self, dimension, order, n_basis, n_verts):
        self._dimension = dimension
        self._order = order
        self._n_basis = n_basis
        self._n_verts = n_verts

        # dof tuple for the dof manager
        self._dof_tuple = (0, 0, 0)

    @property
    def dimension(self):
        """
        The spatial dimension of the element.
        """
        return self._dimension

    @property
    def order(self):
        """
        The polynomial order of the element's basis functions.
        """
        return self._order

    @property
    def n_basis(self):
        """
        The number of basis functions associated with the
        entities of each spatial (sub-) dimenson.
        """
        return self._n_basis

    @property
    def n_verts(self):
        """
        The number of vertices of the element's (sub-) entities
        of each spatial dimension.
        """
        return self._n_verts

    @property
    def dof_tuple(self):
        """
        The number of degrees of freedom associated to the entities
        of every spatial dimension.
        """
        return self._dof_tuple
        
    def eval_basis(self, points, deriv=0):
        """
        Evaluates the element's basis functions or their derivatives
        at given local points on the reference domain.

        Parameters
        ----------

        points : array_like
            The local points at which to evaluate the basis functions

        deriv : int
            The derivation order
        """

        # transfer points to numpy array if necessary
        points = np.atleast_2d(points)

        # check the points' dimensions
        if not points.ndim == 2:
            raise ValueError("Invalid dimension of given points array ({})".format(points.ndim))
        if points.shape[0] > self.dimension:
            raise ValueError("Invalid dimension of given points ({})".format(points.shape[0]))

        # call evaluation method according to derivation order
        if deriv == 0:
            return self._eval_d0basis(points)
        elif deriv == 1:
            return self._eval_d1basis(points)
        elif deriv == 2:
            return self._eval_d2basis(points)
        else:
            raise ValueError("Invalid derivation order ({})".format(deriv))

    def _eval_d0basis(self, points):
        """
        Evaluates the element basis functions.

        Parameters
        ----------

        points : numpy.ndarray
            2d array of local points at which to evaluate the basis functions
        """
        
        raise NotImplementedError("This is an abstract base class!")

    def _eval_d1basis(self, points):
        """
        Evaluates the element basis functions' first derivatives.

        Parameters
        ----------

        points : numpy.ndarray
            2d array of local points at which to evaluate the basis functions
        """
        
        raise NotImplementedError("This is an abstract base class!")

    def _eval_d0basis(self, points):
        """
        Evaluates the element basis functions' second derivatives.

        Parameters
        ----------

        points : numpy.ndarray
            2d array of local points at which to evaluate the basis functions
        """
        
        raise NotImplementedError("This is an abstract base class!")
