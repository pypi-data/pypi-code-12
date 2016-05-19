"""
Provides the data structures that represents a finite element space.
"""

# IMPORTS
import numpy as np

from scipy import sparse

from .manager import DOFManager
from .. import quadrature

# DEBUGGING
from IPython import embed as IPS

class FESpace(DOFManager):
    """
    Base class for all finite element spaces.

    Connects the mesh and reference element via a
    degrees of freedom manager.

    Parameters
    ----------

    mesh : pysofe.meshes.mesh.Mesh
        The mesh used for approximating the pde domain

    element : pysofe.elements.base.Element
        The reference element
    """

    def __init__(self, mesh, element):
        DOFManager.__init__(self, mesh, element)
        
        # get quadrature rule
        self.quad_rule = quadrature.GaussQuadSimp(order=2*element.order,
                                                  dimension=element.dimension)

    def get_quadrature_data(self, d):
        """
        Returns the quadrature points and weighths associated with
        the `d`-dimensional entities as well as the jacobian determinants
        of for integral transformation to the reference domain.

        Parameters
        ----------

        d : int
            The topological dimension of the entities for which to
            return the quadrature data
        """

        # first the quadrature points and weights
        qpoints = self.quad_rule.points[d]
        qweights = self.quad_rule.weights[d]

        if qpoints.size > 0:
            # then the determinants of the reference maps jacobians
            jac_dets = self.mesh.ref_map.jacobian_determinant(points=qpoints)
            
            # but we need the absolute value for integral transformation
            jac_dets = np.abs(jac_dets)
        else:
            # 1d special case
            nE = self.mesh.topology.n_entities[d]
            #jac_dets = np.ndarray(shape=(nE, 0))
            jac_dets = np.ones((nE, 1))

        return qpoints, qweights, jac_dets

    def eval_global_derivatives(self, points, deriv=1):
        """
        Evaluates the global basis functions' derivatives at given local points.

        Parameters
        ----------

        points : array_like
            The local points on the reference element

        deriv : int
            The derivation order

        Returns
        -------

        numpy.ndarray
            (nE x nB x nP x nD [x nD]) array containing for all elements (nE) 
            the evaluation of all basis functions first derivatives (nB) in 
            each point (nP)
        """

        if not deriv in (1, 2):
            msg = "Invalid derivation order for global derivatives! ({})"
            raise ValueError(msg.format(deriv))
        
        # evaluate inverse jacobians of the reference maps for each element
        # and given point
        # --> nE x nP x nD x nD
        inv_jac = self.mesh.ref_map.jacobian_inverse(points)
        
        # get derivatives of the local basis functions at given points
        # --> nB x nP x nD [x nD]
        local_derivatives = self.element.eval_basis(points, deriv)

        # now we decompose the matrix vector product of the inverse jacobian
        # with the local derivatives into an elementwise multiplication and
        # summation along an axis
        # therefore we have to expand some dimensions for the multiplication part
        if deriv == 1:
            derivatives = (inv_jac[:,None,:,:,:] * local_derivatives[None,:,:,:,None]).sum(axis=-2)    # nE x nB x nP x nD
        elif deriv == 2:
            derivatives = (inv_jac.swapaxes(-2,-1)[:,None,:,:,:,None] * local_derivatives[None,:,:,None,:,:]).sum(axis=-2)
            derivatives = (derivatives[:,:,:,:,:,None] * inv_jac[:,None,:,None,:,:]).sum(axis=-2)

        return derivatives

