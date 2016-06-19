
from __future__ import with_statement
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
try:
    # import itertools.imap as map
    import itertools.izip as zip
except ImportError:
    pass
import numpy as np
import pandas as pd
import copy
import collections
from . import constants
from . import utilities
from . import zmat_functions
from . import export
from . import settings
from io import open



class core(object):
    """The main class for dealing with cartesian Coordinates.
    """
    def __init__(self, xyz_frame):
        """How to initialize a Cartesian instance.


        Args:
            xyz_frame (pd.DataFrame): A Dataframe with at least the
                columns ``['atom', 'x', 'y', 'z']``. Where ``'atom'``
                is a string for the elementsymbol.

        Returns:
            Cartesian: A new cartesian instance.

        """
        self.xyz_frame = xyz_frame.copy()
        self.n_atoms = xyz_frame.shape[0]
        # TODO @property for index
        self.index = xyz_frame.index

    def __len__(self):
        return self.n_atoms
