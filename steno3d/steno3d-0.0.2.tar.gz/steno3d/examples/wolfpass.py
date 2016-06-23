"""wolfpass.py is a project example using resources from Wolf Pass"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from os.path import sep

from glob import glob
from numpy import load as npload

from .base import BaseExample
from ..data import DataArray
from ..line import Line
from ..line import Mesh1D
from ..point import Mesh0D
from ..point import Point
from ..project import Project
from ..surface import Mesh2D
from ..surface import Surface
from ..texture import Texture2DImage
from ..volume import Mesh3DGrid
from ..volume import Volume


class Wolfpass(BaseExample):

    def wolfpass_dir(self):
        """base wolfpass directory"""
        return sep.join([self.asset_dir, 'wolfpass'])

    # Borehole Collar Points:
    def collar_point_dir(self):
        """directory for collar points"""
        return sep.join([self.wolfpass_dir, 'collar_point'])

    def collar_vertices(self):
        """collar point vertices"""
        return npload(sep.join([self.collar_point_dir, 'drill_loc_v.npy']))

    def collar_data(self):
        """collar raw data

        list of dicts of 'location' and 'data' with 'title' and 'array'
        """
        raw_data = []
        for npyfile in glob(sep.join([self.collar_point_dir, '*.npy'])):
            if npyfile.endswith('_v.npy'):
                continue
            raw_data += [dict(
                location='N',
                data=DataArray(
                    title=npyfile.split(sep)[-1][:-4],
                    array=npload(npyfile)
                )
            )]
        return raw_data

    def collar_points(self):
        """Steno3D point resource for borehole collars"""
        return Point(
            project=self.project,
            mesh=Mesh0D(
                vertices=self.collar_vertices
            ),
            data=self.collar_data,
            title='Borehole Collar Locations'
        )

    # Borehole Lines:
    def borehole_line_dir(self):
        """directory for borehole lines"""
        return sep.join([self.wolfpass_dir, 'borehole_line'])

    def borehole_vertices(self):
        """borehole line vertices"""
        return npload(sep.join([self.borehole_line_dir, 'boreholes_v.npy']))

    def borehole_segments(self):
        """borehole segment vertex indices"""
        return npload(sep.join([self.borehole_line_dir, 'boreholes_s.npy']))

    def borehole_data(self):
        """borehole raw data

        list of dicts of 'location' and 'data' with 'title' and 'array'
        """
        raw_data = []
        for npyfile in glob(sep.join([self.borehole_line_dir, '*.npy'])):
            if npyfile.endswith('_v.npy') or npyfile.endswith('_s.npy'):
                continue
            raw_data += [dict(
                location='CC',
                data=DataArray(
                    title=npyfile.split(sep)[-1][:-4],
                    array=npload(npyfile)
                )
            )]
        return raw_data

    def borehole_lines(self):
        """Steno3D line resource for boreholes"""
        return Line(
            project=self.project,
            mesh=Mesh1D(
                vertices=self.borehole_vertices,
                segments=self.borehole_segments
            ),
            data=self.borehole_data,
            title='Boreholes'
        )

    # CU Percentage Surfaces:
    def cu_surface_dir(self):
        """directory for CU percent surfaces"""
        return sep.join([self.wolfpass_dir, 'cu_surface'])

    def cu_prefixes(self):
        """list of prefixes for the different cu pct surfaces"""
        return [full_file[:-6] for full_file in
                glob(sep.join([self.cu_surface_dir, '*_v.npy']))]

    def cu_vertices(self):
        """list of cu pct surface vertices"""
        return [npload(prefix + '_v.npy') for prefix in self.cu_prefixes]

    def cu_triangles(self):
        """list of cu pct surface triangles"""
        return [npload(prefix + '_t.npy') for prefix in self.cu_prefixes]

    def cu_surfaces(self):
        """tuple of  Steno3D surface resources for each CU percent range"""
        cu_surfs = tuple()
        for i, prefix in enumerate(self.cu_prefixes):
            cu_surfs += (Surface(
                project=self.project,
                mesh=Mesh2D(
                    vertices=self.cu_vertices[i],
                    triangles=self.cu_triangles[i]
                ),
                title=prefix.split(sep)[-1]
            ),)
        return cu_surfs

    # Lithology Surfaces:
    def lith_surface_dir(self):
        """directory for lithology surfaces"""
        return sep.join([self.wolfpass_dir, 'lith_surface'])

    def lith_prefixes(self):
        """list of prefixes for the different lithology surfaces"""
        return [full_file[:-6] for full_file in
                glob(sep.join([self.lith_surface_dir, '*_v.npy']))]

    def lith_vertices(self):
        """list of lithology surface vertices"""
        return [npload(prefix + '_v.npy') for prefix in self.lith_prefixes]

    def lith_triangles(self):
        """list of lithology surface triangles"""
        return [npload(prefix + '_t.npy') for prefix in self.lith_prefixes]

    def lith_diorite_early_data(self):
        """data for early diorite surface"""
        npyfile = sep.join([self.lith_surface_dir, 'dist_to_borehole.npy'])
        return dict(
            location='N',
            data=DataArray(
                title=npyfile.split(sep)[-1][:-4],
                array=npload(npyfile)
            )
        )

    def lith_surfaces(self):
        """tuple of  Steno3D surface resources for each CU percent range"""
        lith_surfs = tuple()
        for i, prefix in enumerate(self.lith_prefixes):
            if prefix.split(sep)[-1] == 'diorite_early':
                lith_data = [self.lith_diorite_early_data]
            else:
                lith_data = []
            lith_surfs += (Surface(
                project=self.project,
                mesh=Mesh2D(
                    vertices=self.lith_vertices[i],
                    triangles=self.lith_triangles[i]
                ),
                data=lith_data,
                title=prefix.split(sep)[-1]
            ),)
        return lith_surfs

    # Topography Surfaces:
    def topo_surface_dir(self):
        """directory for topography surface"""
        return sep.join([self.wolfpass_dir, 'topo_surface'])

    def topo_vertices(self):
        """topography vertices"""
        return npload(sep.join([self.topo_surface_dir, 'topo_v.npy']))

    def topo_triangles(self):
        """topography triangles"""
        return npload(sep.join([self.topo_surface_dir, 'topo_t.npy']))

    def topo_texture(self):
        """topography surface image texture"""
        return Texture2DImage(
            O=[443200, 491750, 0],
            U=[4425, 0, 0],
            V=[0, 3690, 0],
            image=sep.join([self.topo_surface_dir, 'topography.png'])
        )

    def topo_data(self):
        """elevation data"""
        return dict(
            location='N',
            data=DataArray(
                title='elevation',
                array=npload(sep.join([self.topo_surface_dir,
                                       'Elevation.npy']))
            )
        )

    def topo_surface(self):
        """Steno3D surface resource with topo data and surface imagery"""
        return Surface(
            project=self.project,
            mesh=Mesh2D(
                vertices=self.topo_vertices,
                triangles=self.topo_triangles
            ),
            data=self.topo_data,
            textures=self.topo_texture,
            title='Topography Surface'
        )

    # Cross-section Surface:
    def xsect_surface_dir(self):
        """directory for cross section surfaces"""
        return sep.join([self.wolfpass_dir, 'xsect_surface'])

    def xsect_vertices(self):
        """cross section vertices"""
        return npload(sep.join([self.xsect_surface_dir, 'xsect_v.npy']))

    def xsect_triangles(self):
        """cross section triangles"""
        return npload(sep.join([self.xsect_surface_dir, 'xsect_t.npy']))

    def xsect_data(self):
        """cross section raw data"""
        raw_data = []
        for npyfile in glob(sep.join([self.xsect_surface_dir, '*.npy'])):
            if npyfile.endswith('_v.npy') or npyfile.endswith('_t.npy'):
                continue
            raw_data += [dict(
                location='CC',
                data=DataArray(
                    title=npyfile.split(sep)[-1][:-4],
                    array=npload(npyfile)
                )
            )]
        return raw_data

    def xsect_surface(self):
        """Steno3D surface resource of cross sections"""
        return Surface(
            project=self.project,
            mesh=Mesh2D(
                vertices=self.xsect_vertices,
                triangles=self.xsect_triangles
            ),
            data=self.xsect_data,
            title='Cross-Sections'
        )

    # Lithology Volume:
    def lith_volume_dir(self):
        """directory for lithology volume"""
        return sep.join([self.wolfpass_dir, 'lith_volume'])

    def lith_tensor(self):
        """(h1, h2, h3, x0) for lith volume"""
        return (
            npload(sep.join([self.lith_volume_dir, 'vol_h1.npy'])),
            npload(sep.join([self.lith_volume_dir, 'vol_h2.npy'])),
            npload(sep.join([self.lith_volume_dir, 'vol_h3.npy'])),
            npload(sep.join([self.lith_volume_dir, 'vol_x0.npy']))
        )

    def lith_data(self):
        """raw data for lith volume"""
        raw_data = []
        for npyfile in glob(sep.join([self.lith_volume_dir, '*.npy'])):
            if npyfile.split(sep)[-1].startswith('vol_'):
                continue
            raw_data += [dict(
                location='CC',
                data=DataArray(
                    title=npyfile.split(sep)[-1][:-4],
                    array=npload(npyfile)
                )
            )]
        return raw_data

    def lith_volume(self):
        """Steno3D volume resource of lithology"""
        return Volume(
            project=self.project,
            mesh=Mesh3DGrid(
                h1=self.lith_tensor[0],
                h2=self.lith_tensor[1],
                h3=self.lith_tensor[2],
                x0=self.lith_tensor[3]
            ),
            data=self.lith_data,
            title='Lithology Volume'
        )

    def project(self):
        """empty Steno3D project"""
        return Project(
            title='Wolf Pass'
        )

    def get_resources(self):
        """get a copy of the Wolfpass resources"""
        res = (self.collar_points, self.borehole_lines,)
        res += self.cu_surfaces
        res += self.lith_surfaces
        res += (self.topo_surface, self.xsect_surface, self.lith_volume)
        return res

    def get_project(self):
        """get a copy of the Wolfpass project"""
        return self.get_resources()[0].project[0]
