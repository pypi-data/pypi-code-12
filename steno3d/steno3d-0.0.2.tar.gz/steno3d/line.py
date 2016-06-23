"""line.py contains the Line composite resource for steno3d"""

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


class _Mesh1DOptions(MeshOptions):
    pass


class _LineOptions(ColorOptions):
    pass


class Mesh1D(BaseMesh):
    """Contains spatial information of a 1D line set"""
    vertices = properties.Array(
        'Mesh vertices',
        shape=('*', 3),
        dtype=float,
        required=True
    )
    segments = properties.Array(
        'Segment endpoint indices',
        shape=('*', 2),
        dtype=int,
        required=True
    )
    opts = properties.Pointer(
        'Options',
        ptype=_Mesh1DOptions
    )

    def __init__(self, *args, **kwargs):
        super(Mesh1D, self).__init__(*args, **kwargs)
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
            self._nC = len(self.segments)
        return self._nC

    @properties.validator
    def validate(self):
        """Check if mesh content is built correctly"""
        if npmin(self.segments) < 0:
            raise ValueError('Segments may only have positive integers')
        if npmax(self.segments) >= len(self.vertices):
            raise ValueError('Segments expects more vertices than provided')
        return True

    @property
    def _files(self):
        """Get the file information"""
        files = {
            'vertices': self._properties['vertices'].serialize(self.vertices),
            'segments': self._properties['segments'].serialize(self.segments),
        }
        return files


class _LineBinder(properties.PropertyClass):
    """Contains the data on a 1D line set with location information"""
    location = properties.String(
        'Location of the data on mesh',
        required=True,
        choices={
            'CC': ('LINE', 'FACE', 'CELLCENTER', 'EDGE', 'SEGMENT'),
            'N': ('VERTEX', 'NODE', 'ENDPOINT')
        }
    )
    data = properties.Pointer(
        'Data',
        ptype='DataArray',
        required=True
    )


class Line(CompositeResource):
    """Contains all the information about a 1D line set"""
    mesh = properties.Pointer(
        'Mesh',
        ptype=Mesh1D,
        required=True
    )
    data = properties.Pointer(
        'Data',
        ptype=_LineBinder,
        repeated=True
    )
    opts = properties.Pointer(
        'Options',
        ptype=_LineOptions
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
                    'line.data[{index}] length {datalen} does not match '
                    '{loc} length {meshlen}'.format(
                        index=ii,
                        datalen=len(dat.data.array),
                        loc=dat.location,
                        meshlen=valid_length
                    )
                )
        super(Line, self).validate()
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


__all__ = ['Line', 'Mesh1D']
