"""
PyCPG
===
    Code to read cgp files without needing the python wrapping from the
    original CGP code that brings hdf5-library in a state where it crashes
    when opening files with h5py.
"""

from .cgp_config import coordinate_type
from .geometry_reader import GeometryReader
from .topological_point_set import TopologicalPointSet
from .cartesian_point_set import CartesianPointSet


__author__ = 'Tobias Maier <tobias.maier@unibas.ch>'
__all__ = []
__version__ = '0.1dev'
