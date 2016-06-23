"""point.py contains the Point composite resource for steno3d"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from json import dumps
import properties

from .base import BaseMesh
from .base import CompositeResource
from .options import ColorOptions
from .options import MeshOptions


class _Mesh0DOptions(MeshOptions):
    pass


class _PointOptions(ColorOptions):
    pass


class Mesh0D(BaseMesh):
    """Contains spatial information of a 0D point cloud."""
    vertices = properties.Array(
        'Point locations',
        shape=('*', 3),
        dtype=float,
        required=True
    )
    opts = properties.Pointer(
        'Mesh0D Options',
        ptype=_Mesh0DOptions
    )

    def __init__(self, *args, **kwargs):
        super(Mesh0D, self).__init__(*args, **kwargs)
        self._nN = None

    @properties.validator
    def validate(self):
        """Check if mesh content is built correctly"""
        return True

    @property
    def nN(self):
        """ get number of nodes """
        if getattr(self, '_nN', None) is None:
            self._nN = len(self.vertices)
        return self._nN

    @property
    def _files(self):
        """Get the file information"""
        files = {
            'vertices': self._properties['vertices'].serialize(self.vertices),
        }
        return files


class _PointBinder(properties.PropertyClass):
    """Contains the data on a 0D point cloud"""
    location = properties.String(
        'Location of the data on mesh',
        default='N',
        required=True,
        choices={
            'N': ('NODE', 'CELLCENTER', 'CC', 'VERTEX')
        }
    )
    data = properties.Pointer(
        'Data',
        ptype='DataArray',
        required=True
    )


class Point(CompositeResource):
    """Contains all the information about a 0D point cloud"""
    mesh = properties.Pointer(
        'Mesh',
        ptype=Mesh0D,
        required=True
    )
    data = properties.Pointer(
        'Data',
        ptype=_PointBinder,
        repeated=True
    )
    textures = properties.Pointer(
        'Textures',
        ptype='Texture2DImage',
        repeated=True
    )
    opts = properties.Pointer(
        'Options',
        ptype=_PointOptions
    )

    @properties.validator
    def validate(self):
        """Check if resource is built correctly"""
        for ii, dat in enumerate(self.data):
            assert dat.location == 'N'
            valid_length = self.mesh.nN
            if len(dat.data.array) != valid_length:
                raise ValueError(
                    'point.data[{index}] length {datalen} does not match '
                    '{loc} length {meshlen}'.format(
                        index=ii,
                        datalen=len(dat.data.array),
                        loc=dat.location,
                        meshlen=valid_length
                    )
                )
        super(Point, self).validate()
        return True

    @property
    def _reqdata(self):
        """Get the required longUids"""
        datadict = {
            'mesh': dumps({
                'uid': self.mesh.json_after_upload['longUid'],
            }),
            'data': dumps([
                {
                    'location': d.location,
                    'uid': d.data.json_after_upload['longUid'],
                } for d in self.data
            ]),
            'textures': dumps([
                {
                    'uid': t.json_after_upload['longUid'],
                } for t in self.textures
            ]),
        }
        return datadict


__all__ = ['Point', 'Mesh0D']
