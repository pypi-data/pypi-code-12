"""mics.py contains miscellaneous files and components to supplement
Steno3D examples
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from os.path import sep

from .base import BaseExample


class Images(BaseExample):
    """Class containing miscellaneous image files."""

    def metal(self):
        """metal texture png"""
        return sep.join([self.asset_dir, 'basic', 'metal.png'])

    def wood(self):
        """wood texture png"""
        return sep.join([self.asset_dir, 'basic', 'woodplanks.png'])

try:
    del absolute_import, division, print_function, unicode_literals
except NameError:
    # Error cleaning namespace
    pass
