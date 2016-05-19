"""
Provides the base class for all pde objects.
"""

# IMPORTS
import numpy as np
from scipy import sparse

import conditions

# DEBUGGING
from IPython import embed as IPS

class PDE(object):
    """
    Base class for all partial differential equations.

    Parameters
    ----------

    fe_space : pysofe.spaces.space.FESpace
        The function space of the pde

    bc : pysofe.pde.conditions.BoundaryCondition, iterable
        The boundary condition(s)
    """

    def __init__(self, fe_space, bc):
        self.fe_space = fe_space

        if isinstance(bc, conditions.BoundaryCondition):
            self.bc = (bc,)
        else:
            self.bc = tuple(bc)

        # initialize stiffness matrix and load vector
        self.stiffness = None
        self.load = None

        # we don't have a solution yet
        self.solution = None

    def assemble(self):
        """
        Assembles all discrete operators that are part of the pde.
        """
        raise NotImplementedError()

    def apply_conditions(self):
        """
        Applies the boundary conditions to the stiffness matrix
        and load vector.
        """

        A = self.stiffness
        b = self.load
        
        for bc in self.bc:
            A, b = bc.apply(A, b)

        self.stiffness = A
        self.load = b

    def solve(self):
        """
        Solves the partial differential equation.
        """
        raise NotImplementedError()
