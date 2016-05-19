"""
Provides data structures that represent weak forms differential operators.
"""

# IMPORTS
import numpy as np
from scipy import sparse

# DEBUGGING
from IPython import embed as IPS

class Operator(object):
    """
    Base class for all operators.

    Derived classes have to implement the method 
    :py:meth:`_compute_entries()`

    Parameters
    ----------

    fe_space : pysofe_light.spaces.space.FESpace
        A function space the operator works on
    """

    def __init__(self, fe_space):
        self.fe_space = fe_space
        
    def assemble(self, codim=0, mask=None):
        """
        Assembles the discrete weak operator.

        Parameters
        ----------

        codim : int
            The codimension of the entities for which to assemble

        mask : array_like
            Boolean 1d array marking specific entities for assembling

        Returns
        -------

        scipy.sparse.lil_matrix
        """

        # first compute the operator specific entries
        # --> nE x nB [x nB]
        entries = self._compute_entries(codim=codim)

        # get the dof map for the desired entities
        # --> nB x nE
        dim = self.fe_space.mesh.dimension - codim
        dof_map = self.fe_space.get_dof_map(d=dim, mask=mask)
        n_dof = self.fe_space.n_dof

        # apply masking if neccessary
        if mask is not None:
            assert mask.ndim == 1
            assert mask.dtype == bool

            entries = entries.compress(mask, axis=0)
            dof_map = dof_map.compress(mask, axis=1)

        # get row and column indices for coo matrix
        # depending on whether to assemble vector or matrix
        if entries.ndim == 2:
            row_ind = dof_map.ravel(order='F')
            col_ind = np.ones_like(row_ind)
            shape = (n_dof, 1)
        elif entries.ndim == 3:
            nB = np.size(entries, axis=1)
            row_ind = np.tile(dof_map, reps=(nB, 1)).ravel(order='F')
            col_ind = np.repeat(dof_map, repeats=nB, axis=0).ravel(order='F')
            shape = (n_dof, n_dof)

        # make entries 1-dimensional
        entries = entries.ravel(order='C') #!!!

        # apply minimum rule
        # (if elements have different polynomial degrees)
        non_zero_dof = (row_ind * col_ind) != 0
        entries = entries.compress(non_zero_dof)
        row_ind = row_ind.compress(non_zero_dof) - 1
        col_ind = col_ind.compress(non_zero_dof) - 1

        # assemble discrete operator
        M = sparse.coo_matrix((entries, (row_ind, col_ind)), shape=shape)

        return M.tolil()

    def _compute_entries(self, codim=0):
        """
        Computes the entries for the discrete form of the operator.

        Parameters
        ----------

        codim : int
            The codimension of the considered entities

        Returns
        -------

        numpy.ndarray
            nE x nB x (nB|1)
        """
        raise NotImplementedError()

class MassMatrix(Operator):
    """
    Represents the operator

    .. math::
       \\int_{\\Omega} c uv

    where :math:`u,v \\in V` and :math:`c \\in L^{2}`.

    Parameters
    ----------

    fe_space : pysofe_light.spaces.space.FESpace
        The function space the operator works on

    c : scalar, callable
        The function factor
    """

    def __init__(self, fe_space, c=1):
        Operator.__init__(self, fe_space)
        self.c = c

    def _compute_entries(self, codim=0):
        dim = self.fe_space.mesh.dimension - codim
        
        # first, we need the quadrature points and weights
        # for numerical integration and the jacobian determinants
        # of the reference maps resulting from integral transformation
        # to the referende domain
        qpoints, qweights, jac_dets = self.fe_space.get_quadrature_data(d=dim)

        # next, we evaluate the function factor
        C = self.fe_space.mesh.eval_function(fnc=self.c, points=qpoints)

        # for consistency check
        nE = jac_dets.shape[0]

        if qpoints.size > 0:
            nP = qpoints.shape[1]
            assert C.shape == (nE, nP)

            basis = self.fe_space.element.eval_basis(points=qpoints, deriv=0)
            values = basis[None,None,:,:] * basis[None,:,None,:]
        else:
            # 1D special case
            assert C.shape == (nE, 1)
            
            #nB = self.fe_space.element.n_basis[0]
            nB = 1
            values = np.ones((nB, nB, 1))[None,:,:,:]

        jac_dets = jac_dets[:,None,None,:]
        qweights = qweights[None,None,None,:]
        C = C[:,None,None,:]

        entries = (C * values * jac_dets * qweights).sum(axis=-1)

        return entries

class L2Product(Operator):
    """
    Represents the operator

    .. math::
       \\int_{\\Omega} fv

    where :math:`v \\in V` and :math:`f \\in L^{2}`.

    Parameters
    ----------

    fe_space : pysofe_light.spaces.space.FESpace
        The function space the operator works on

    f : scalar, callable
        The function factor
    """

    def __init__(self, fe_space, f=1):
        Operator.__init__(self, fe_space)
        self.f = f

    def _compute_entries(self, codim=0):
        dim = self.fe_space.mesh.dimension - codim
        
        # first, we need the quadrature points and weights
        # for numerical integration and the jacobian determinants
        # of the reference maps resulting from integral transformation
        # to the referende domain
        qpoints, qweights, jac_dets = self.fe_space.get_quadrature_data(d=dim)

        # next, we evaluate the function factor
        F = self.fe_space.mesh.eval_function(fnc=self.f, points=qpoints)

        # for consistency check
        nE = jac_dets.shape[0]

        if qpoints.size > 0:
            nP = qpoints.shape[1]
            assert F.shape == (nE, nP)

            basis = self.fe_space.element.eval_basis(points=qpoints, deriv=0)
            values = basis[None,:,:]
        else:
            # 1D special case
            assert F.shape == (nE, 1)
            
            #nB = self.fe_space.element.n_basis[0]
            nB = 1
            values = np.ones((nB, 1))[None,:,:]

        # now, compute the entries
        jac_dets = jac_dets[:,None,:]
        qweights = qweights[None,None,:]
        F = F[:,None,:]

        entries = (F * values * jac_dets * qweights).sum(axis=-1)

        return entries

class Laplacian(Operator):
    """
    Represents the operator
    
    .. math::
       \\int_{\\Omega} a \\nabla u \\cdot \\nabla v

    where :math:`u,v \\in V` and :math:`a \\in L^{2}`.

    Parameters
    ----------

    fe_space : pysofe_light.spaces.space.FESpace
        The function space the operator works on

    a : scalar, callable
        The function factor
    """

    def __init__(self, fe_space, a=1):
        Operator.__init__(self, fe_space)
        self.a = a

    def _compute_entries(self, codim=0):
        dim = self.fe_space.mesh.dimension - codim
        
        # first, we need the quadrature points and weights
        # for numerical integration and the jacobian determinants
        # of the reference maps resulting from integral transformation
        # to the referende domain
        qpoints, qweights, jac_dets = self.fe_space.get_quadrature_data(d=dim)

        # next, we evaluate the function factor
        A = self.fe_space.mesh.eval_function(fnc=self.a, points=qpoints)

        # now, compute the entries
        dbasis = self.fe_space.eval_global_derivatives(points=qpoints, deriv=1)

        # consistency check
        nE = jac_dets.shape[0]
        nP = qpoints.shape[1]
        nD = self.fe_space.mesh.dimension
        assert A.shape in {(nE, nP), (nE, nP, nD, nD)}
        
        if (A.ndim - 2) == 0:
            # assuming `a` to be scalar
            values = (dbasis[:,None,:,:,:] * dbasis[:,:,None,:,:]).sum(axis=-1)
            values *= A[:,None,None,:]
        elif (A.ndim - 2) == 2:
            # assuming `a` to be matrix
            Adbasis = (A[:,None,:,:,:] * dbasis[:,:,:,None,:]).sum(axis=-1)
            values = (Adbasis[:,None,:,:,:] * dbasis[:,:,None,:,:]).sum(axis=-1)
        else:
            raise ValueError("Invalid shape of function factor ({})".format(A.shape))

        jac_dets = jac_dets[:,None,None,:]
        qweights = qweights[None,None,None,:]

        entries = (values * jac_dets * qweights).sum(axis=-1)

        return entries

class L2Projection(object):
    """
    Provides an object for the :math:`L^{2}`\ -projection
    of a given function.
    """

    @staticmethod
    def project(fnc, fe_space, codim=0, mask=None):
        """
        Projects the given function to the given finite element space.

        Parameters
        ----------

        fnc : scalar, callable
            The function to project

        fe_space
            The function space onto which to project

        codim : int
            The codimension of the considered entities

        mask : array_like
            Boolean array marking entities onto which to project
        """

        # we need a l2 product and a mass matrix for this
        l2_product = L2Product(fe_space, fnc)
        mass_matrix = MassMatrix(fe_space)

        # assemble the discrete versions
        F = l2_product.assemble(codim, mask).tocsr()
        M = mass_matrix.assemble(codim, mask).tocsr()

        # allocate memory
        U = np.zeros(np.size(F))

        dim = fe_space.mesh.dimension - codim
        dof_map = fe_space.get_dof_map(d=dim)
        I = np.setdiff1d(np.unique(dof_map), 0) - 1

        U[I] = sparse.linalg.spsolve(M[I,:][:,I], F[I])

        return U
