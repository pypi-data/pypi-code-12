"""texture.py contains the texture resource structures"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple
from json import dumps
import properties

from .base import BaseTexture2D


FileProp = namedtuple('FileProp', ['file', 'dtype'])


class Texture2DImage(BaseTexture2D):
    """Contains an image that can be mapped to a 2D surface"""

    _resource_class = 'image'

    O = properties.Vector(
        'Origin of the texture',
        required=True
    )
    U = properties.Vector(
        'U axis of the texture',
        required=True
    )
    V = properties.Vector(
        'V axis of the texture',
        required=True
    )
    image = properties.Image(
        'Image file',
        required=True
    )

    @properties.validator
    def validate(self):
        """Check if mesh content is built correctly"""
        if self.O.nV != 1 or self.U.nV != 1 or self.V.nV != 1:
            raise ValueError('O, U, and V must each be only one vector')
        return True

    @property
    def _files(self):
        """Get the file information"""
        self.image.seek(0)
        files = {
            'image': FileProp(self.image, 'png')
        }
        return files

    @property
    def _reqdata(self):
        datadict = {
            'OUV': dumps(dict(
                O=[self.O[0][0], self.O[0][1], self.O[0][2]],
                U=[self.U[0][0], self.U[0][1], self.U[0][2]],
                V=[self.V[0][0], self.V[0][1], self.V[0][2]],
            )),
        }
        return datadict

    def _repr_png_(self):
        """For IPython display"""
        if self.image is None:
            return None
        self.image.seek(0)
        return self.image.read()


__all__ = ['Texture2DImage']
