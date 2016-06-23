from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from os.path import sep

from json import loads
from numpy import array
from numpy import mean

from .base import BaseExample
from ..data import DataArray
from ..project import Project
from ..surface import Mesh2D
from ..surface import Surface
from ..texture import Texture2DImage


class Topography(BaseExample):

    def file_base(self):
        """topography file base"""
        return sep.join([self.asset_dir, 'basic', 'topography'])

    def data(self):
        """topography data from json"""
        with open(self.file_base + '.json', 'r') as f:
            data = loads(f.read())
        return data

    def vertices(self):
        """n x 3 topography vertices"""
        return array(self.data['vertices'])

    def triangles(self):
        """n x 3 topography triangles"""
        return array(self.data['triangles'])

    def texture(self):
        """topography surface image texture"""
        return Texture2DImage(
            O=[443200, 491750, 0],
            U=[4425, 0, 0],
            V=[0, 3690, 0],
            image=self.file_base + '.png'
        )

    def vertex_elevation(self):
        """z-coordinate of vertex"""
        return self.vertices[:, 2]

    def vertex_elevation_data(self):
        """elevation as Steno3D data"""
        return DataArray(
            array=self.vertex_elevation,
            title='Elevation, vertices'
        )

    def face_elevation(self):
        """average z-coordinate of face"""
        return mean(self.vertex_elevation[self.triangles], axis=1)

    def face_elevation_data(self):
        """elevation as Steno3D data"""
        return DataArray(
            array=self.face_elevation,
            title='Elevation, faces'
        )

    def surface(self):
        """ground surface with topo data and surface imagery"""
        return Surface(
            project=self.project,
            mesh=Mesh2D(
                vertices=self.vertices,
                triangles=self.triangles
            ),
            data=[
                dict(
                    location='N',
                    data=self.vertex_elevation_data
                ),
                dict(
                    location='CC',
                    data=self.face_elevation_data
                )
            ],
            textures=self.texture,
            title='Topography Surface',
            description=('This surface has face and vertex elevation '
                         'data as well as surface imagery')
        )

    def project(self):
        """empty Steno3D project"""
        return Project(
            title='Topography and Surface Imagery'
        )

    def get_resources(self):
        """get a copy of the topography resources

        tuple(topography surface,)
        """
        return (self.surface,)

    def get_project(self):
        """get a copy of the topography project"""
        return self.get_resources()[0].project[0]
