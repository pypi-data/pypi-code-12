"""data.py contains resource data structures"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import properties

from .base import BaseData


class DataArray(BaseData):
    """Data array with unique values at every point in the mesh"""
    _resource_class = 'array'
    array = properties.Array(
        'Data, unique values at every point in the mesh',
        shape=('*',),
        dtype=(float, int)
    )

    def __init__(self, array=None, **kwargs):
        super(DataArray, self).__init__(**kwargs)
        if array is not None:
            self.array = array

    def validate(self):
        """Check if content is built correctly"""
        return True

    @property
    def _files(self):
        """Get the file information"""
        files = {
            'array': self._properties['array'].serialize(self.array),
        }
        return files

__all__ = ['DataArray']
