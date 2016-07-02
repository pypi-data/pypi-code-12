"""
Sile object for reading/writing GULP in/output
"""
from __future__ import print_function

# Import sile objects
from .sile import SileGULP
from ..sile import *

# Import the geometry object
from sisl import Geometry, Atom, SuperCell
from sisl.quantity import DynamicalMatrix

import numpy as np

__all__ = ['GULPresSile']


class GULPresSile(SileGULP):
    """ GULP output file object """

    def _setup(self):
        """ Setup `GULPresSile` after initialization """

    @Sile_fh_open
    def read_sc(self, *args, **kwargs):
        """ Reads a `SuperCell` and creates the GULP cell """

        f, _ = self.step_to('cell')
        if not f:
            raise ValueError(
                ('GULPSile tries to lookup the SuperCell vectors. '
                 'This could not be found found in file: "' + self.file + '".'))

        # skip 1 line
        cell = map(float, self.readline())

        return SuperCell(cell)

    @Sile_fh_open
    def read_geom(self, *args, **kwargs):
        """ Reads a geometry and creates the GULP dynamical geometry """

        sc = self.read_sc(*args, **kwargs)

        f, _ = self.step_to('fractional')
        

        # Return the geometry
        return Geometry(xyz, atoms=Atom[Z], sc=sc)


add_sile('res', GULPresSile, gzip=True)
