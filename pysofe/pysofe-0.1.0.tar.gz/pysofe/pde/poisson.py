"""
Provides the data structure that represents the Poisson equation.
"""

# IMPORTS

from .base import PDE
from ..spaces import operators

from scipy.sparse import linalg as sparse_linalg

# DEBUGGING
from IPython import embed as IPS

class Poisson(PDE):
    """
    Represents the linear Poisson equation

    .. math::
       - a \Delta u = f
    
    Parameters
    ----------
    
    fe_space : pysofe.spaces.space.FESpace
        The considered function space
    
    a : callable
        The coefficient function
    
    f : callable
        The right hand site function
    
    bc : pysofe.pde.conditions.BoundaryCondition, iterable
        The boundary condition(s)
    """

    def __init__(self, fe_space, a=1., f=0., bc=None):
        PDE.__init__(self, fe_space, bc)

        # get operators
        self._laplacian = operators.Laplacian(fe_space, a)
        self._l2product = operators.L2Product(fe_space, f)

    def assemble(self):
        # compute stiffnes matrix and load vector
        self.stiffness = self._laplacian.assemble(codim=0, mask=None)
        self.load = self._l2product.assemble(codim=0, mask=None)

        # apply boundary conditions
        self.apply_conditions()

    def solve(self):
        # first, assemble the system
        self.assemble()

        # next, transform matrix formats for faster arithmetic
        rhs = self.stiffness.tocsr()
        lhs = self.load.tocsr()

        # then, solve the discrete system
        self.solution = sparse_linalg.spsolve(rhs, lhs)

        return self.solution
