"""
PySOFE
======

A simple and sophisticated object oriented flexible finite element
environment for the solution of partial differential equations written
in python.

"""

# current version
__version__ = '0.1.0'

import elements
import meshes
import quadrature
import spaces
import pde
import utils
import visualization

from .elements import P1, P2
from .meshes import Mesh, UnitSquareMesh
from .spaces import FESpace
from .pde import Poisson, DirichletBC
from .visualization import show
