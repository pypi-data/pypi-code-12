"""teapot.py provides an example Steno3D project of a teapot"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from os.path import sep

from json import loads
from numpy import array

from .base import BaseExample
from ..point import Mesh0D
from ..point import Point
from ..project import Project
from ..surface import Mesh2D
from ..surface import Surface


class Teapot(BaseExample):
    """Class containing components of teapot project. Components can be
    viewed individually or copied into new resources or projects with
    get_resources() and get_project(), respectively.
    """

    def file(self):
        """teapot json file"""
        return sep.join([self.asset_dir, 'basic', 'teapot.json'])

    def data(self):
        """teapot data read from json"""
        with open(self.file, 'r') as f:
            file_data = loads(f.read())
        return file_data

    def vertices(self):
        """n x 3 numpy array of teapot vertices"""
        return array(self.data['vertices'])

    def triangles(self):
        """n x 3 numpy array of teapot triangle vertex indices"""
        return array(self.data['triangles'])

    def points(self):
        """Steno3D points at teapot vertices"""
        return Point(
            project=self.project,
            mesh=Mesh0D(
                vertices=self.vertices
            ),
            title='Teapot Vertex Points'
        )

    def surface(self):
        """Steno3D teapot surface"""
        return Surface(
            project=self.project,
            mesh=Mesh2D(
                vertices=self.vertices,
                triangles=self.triangles
            ),
            title='Teapot Surface'
        )

    def project(self):
        """empty Steno3D project"""
        return Project(
            title='Teapot project',
            description='Project with surface and points at vertices'
        )

    def get_resources(self):
        """get a copy of teapot resources.

        tuple(teapot surface, teapot points,)
        """
        return (self.surface, self.points,)

    def get_project(self):
        """get a copy of teapot project."""
        return self.get_resources()[0].project[0]
