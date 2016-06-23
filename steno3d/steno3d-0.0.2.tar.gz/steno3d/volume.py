"""volume.py contains the Volume composite resource for steno3d"""

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


class _Mesh3DOptions(MeshOptions):
    pass


class _VolumeOptions(ColorOptions):
    pass


class Mesh3DGrid(BaseMesh):
    """Contains spatial information of a 3D grid volume."""

    h1 = properties.Array(
        'Tensor cell widths, x-direction',
        shape=('*',),
        dtype=float,
        required=True
    )
    h2 = properties.Array(
        'Tensor cell widths, y-direction',
        shape=('*',),
        dtype=float,
        required=True
    )
    h3 = properties.Array(
        'Tensor cell widths, z-direction',
        shape=('*',),
        dtype=float,
        required=True
    )
    x0 = properties.Vector(
        'Origin vector',
        default=[0, 0, 0]
    )
    opts = properties.Pointer(
        'Mesh3D Options',
        ptype=_Mesh3DOptions
    )

    def __init__(self, *args, **kwargs):
        super(Mesh3DGrid, self).__init__(*args, **kwargs)
        self._nN = None
        self._nC = None

    @property
    def nN(self):
        """ get number of nodes """
        if getattr(self, '_nN', None) is None:
            self._nN = (
                (len(self.h1)+1) * (len(self.h2)+1) * (len(self.h3)+1)
            )
        return self._nN

    @property
    def nC(self):
        """ get number of cells """
        if getattr(self, '_nC', None) is None:
            self._nC = len(self.h1) * len(self.h2) * len(self.h3)
        return self._nC

    @properties.validator
    def validate(self):
        """Check if mesh content is built correctly"""
        if self.x0.nV != 1:
            raise ValueError('Origin x0 must be only one vector')
        return True

    @property
    def _reqdata(self):
        """Get the required longUids"""
        datadict = {
            'tensors': dumps(dict(
                h1=self.h1.tolist(),
                h2=self.h2.tolist(),
                h3=self.h3.tolist(),
            )),
            'OUVZ': dumps(dict(
                O=self.x0.tolist()[0],
                U=[self.h1.sum(), 0, 0],
                V=[0, self.h2.sum(), 0],
                Z=[0, 0, self.h3.sum()],
            )),
        }
        return datadict


class _VolumeBinder(properties.PropertyClass):
    """Contains the data on a 3D volume with location information"""
    location = properties.String(
        'Location of the data on mesh',
        required=True,
        choices={
            'CC': ('CELLCENTER'),
            'N': ('NODE', 'VERTEX', 'CORNER')
        }
    )
    data = properties.Pointer(
        'Data',
        ptype='DataArray',
        required=True
    )


class Volume(CompositeResource):
    """Contains all the information about a 3D volume"""
    mesh = properties.Pointer(
        'Mesh',
        ptype=Mesh3DGrid,
        required=True
    )
    data = properties.Pointer(
        'Data',
        ptype=_VolumeBinder,
        repeated=True
    )
    opts = properties.Pointer(
        'Options',
        ptype=_VolumeOptions
    )

    @properties.validator
    def validate(self):
        """Check if resource is built correctly"""
        for ii, dat in enumerate(self.data):
            assert dat.location in ('N', 'CC')
            valid_length = (
                self.mesh.nC if dat.location == 'CC'
                else self.mesh.nN
            )
            if len(dat.data.array) != valid_length:
                raise ValueError(
                    'volume.data[{index}] length {datalen} does not match '
                    '{loc} length {meshlen}'.format(
                        index=ii,
                        datalen=len(dat.data.array),
                        loc=dat.location,
                        meshlen=valid_length
                    )
                )
        super(Volume, self).validate()
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
        }
        return datadict


__all__ = ['Volume', 'Mesh3DGrid']
