"""surface.py contains the Surface composite resource for steno3d"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from json import dumps
from numpy import max as npmax
from numpy import min as npmin
import properties

from .base import BaseMesh
from .base import CompositeResource
from .options import ColorOptions
from .options import MeshOptions


class _Mesh2DOptions(MeshOptions):
    pass


class _SurfaceOptions(ColorOptions):
    pass


class Mesh2D(BaseMesh):
    """class steno3d.Mesh2D

    Contains spatial information about a 2D surface defined by
    triangular faces.
    """
    vertices = properties.Array(
        'Mesh vertices',
        shape=('*', 3),
        dtype=float,
        required=True
    )
    triangles = properties.Array(
        'Mesh triangle vertex indices',
        shape=('*', 3),
        dtype=int,
        required=True
    )
    opts = properties.Pointer(
        'Mesh2D Options',
        ptype=_Mesh2DOptions
    )

    def __init__(self, *args, **kwargs):
        super(Mesh2D, self).__init__(*args, **kwargs)
        self._nN = None
        self._nC = None

    @property
    def nN(self):
        """ get number of nodes """
        if getattr(self, '_nN', None) is None:
            self._nN = len(self.vertices)
        return self._nN

    @property
    def nC(self):
        """ get number of cells """
        if getattr(self, '_nC', None) is None:
            self._nC = len(self.triangles)
        return self._nC

    @properties.validator
    def validate(self):
        """Check if mesh content is built correctly"""
        if npmin(self.triangles) < 0:
            raise ValueError('Triangles may only have positive integers')
        if npmax(self.triangles) >= len(self.vertices):
            raise ValueError('Triangles expects more vertices than provided')
        return True

    @property
    def _files(self):
        """Get the file information"""
        files = {
            'triangles':
                self._properties['triangles'].serialize(self.triangles),
            'vertices': self._properties['vertices'].serialize(self.vertices),
        }
        return files


class Mesh2DGrid(BaseMesh):
    """Contains spatial information of a 2D grid."""
    h1 = properties.Array(
        'Grid cell widths, x-direction',
        shape=('*',),
        dtype=float,
        required=True
    )
    h2 = properties.Array(
        'Grid cell widths, y-direction',
        shape=('*',),
        dtype=float,
        required=True
    )
    x0 = properties.Vector(
        'Origin vector',
        default=[0, 0, 0]
    )
    Z = properties.Array(
        'Node topography',
        shape=('*',),
        dtype=float
    )
    opts = properties.Pointer(
        'Mesh2D Options',
        ptype=_Mesh2DOptions
    )

    def __init__(self, *args, **kwargs):
        super(Mesh2DGrid, self).__init__(*args, **kwargs)
        self._nN = None
        self._nC = None

    @property
    def nN(self):
        """ get number of nodes """
        if getattr(self, '_nN', None) is None:
            self._nN = (len(self.h1)+1) * (len(self.h2)+1)
        return self._nN

    @property
    def nC(self):
        """ get number of cells """
        if getattr(self, '_nC', None) is None:
            self._nC = len(self.h1) * len(self.h2)
        return self._nC

    @properties.validator
    def validate(self):
        """Check if mesh content is built correctly"""
        if self.x0.nV != 1:
            raise ValueError('Origin x0 must be only one vector')
        if getattr(self, 'Z', None) is not None and len(self.Z) != self.nN:
            raise ValueError(
                'Length of Z, {zlen}, must equal number of nodes, '
                '{nnode}'.format(
                    zlen=len(self.Z),
                    nnode=self.nN
                )
            )
        return True

    @property
    def _reqdata(self):
        """Get the required longUids"""
        datadict = {
            'tensors': dumps(dict(
                h1=self.h1.tolist(),
                h2=self.h2.tolist(),
            )),
            'OUV': dumps(dict(
                O=self.x0.tolist()[0],
                U=[self.h1.sum(), 0, 0],
                V=[0, self.h2.sum(), 0],
            )),
        }
        return datadict

    @property
    def _files(self):
        """Get the file information"""
        if getattr(self, 'Z', None) is None:
            return {}
        files = {
            'Z': self._properties['Z'].serialize(self.Z),
        }
        return files


class _SurfaceBinder(properties.PropertyClass):
    """Contains the data on a 2D surface with location information"""
    location = properties.String(
        'Location of the data on mesh',
        required=True,
        choices={
            'CC': ('FACE', 'CELLCENTER'),
            'N': ('NODE', 'VERTEX', 'CORNER')
        }
    )
    data = properties.Pointer(
        'Data',
        ptype='DataArray',
        required=True
    )


class Surface(CompositeResource):
    """Contains all the information about a 2D surface"""
    mesh = properties.Pointer(
        'Mesh',
        ptype=[Mesh2D, Mesh2DGrid],
        required=True
    )
    data = properties.Pointer(
        'Data',
        ptype=_SurfaceBinder,
        repeated=True
    )
    textures = properties.Pointer(
        'Textures',
        ptype='Texture2DImage',
        repeated=True
    )
    opts = properties.Pointer(
        'Options',
        ptype=_SurfaceOptions
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
                    'surface.data[{index}] length {datalen} does not match '
                    '{loc} length {meshlen}'.format(
                        index=ii,
                        datalen=len(dat.data.array),
                        loc=dat.location,
                        meshlen=valid_length
                    )
                )
        super(Surface, self).validate()
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


__all__ = ['Surface', 'Mesh2D', 'Mesh2DGrid']
