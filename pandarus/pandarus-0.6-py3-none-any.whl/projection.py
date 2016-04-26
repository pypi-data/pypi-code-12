# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from functools import partial
from itertools import starmap
import pyproj
import shapely.geometry as sg

# License text as some code is copied directly
# Copyright (c) 2007, Sean C. Gillies
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Sean C. Gillies nor the names of
#       its contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

WGS84 = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
# See also http://spatialreference.org/ref/esri/54009/
# and http://cegis.usgs.gov/projection/pdf/nmdrs.usery.prn.pdf
MOLLWEIDE = "+proj=moll +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"


def wgs84(s):
    """Fix no CRS or fiona giving abbreviated wgs84 definition."""
    if not s:
        return WGS84
    elif s == "+no_defs":
        return WGS84
    else:
        return s


def project(geom, from_proj=None, to_proj=None):
    """
Project a ``shapely`` geometry, and returns a new geometry of the same type from the transformed coordinates.

Default input projection is `WGS84 <https://en.wikipedia.org/wiki/World_Geodetic_System>`_, default output projection is `Mollweide <http://spatialreference.org/ref/esri/54009/>`_.

Borrowed and adapted from `mfussenegger <https://github.com/mfussenegger/Shapely/>`_.

Inputs:
    *geom*: A ``shapely`` geometry.
    *from_proj*: A ``PROJ4`` string. Optional.
    *to_proj*: A ``PROJ4`` string. Optional.

Returns:
    A ``shapely`` geometry.

    """
    from_proj = wgs84(from_proj)
    to_proj = wgs84(to_proj)
    projection_func = partial(
        pyproj.transform,
        pyproj.Proj(from_proj),
        pyproj.Proj(to_proj)
    )

    if geom.type in ('Point', 'LineString', 'Polygon'):
        # Applies the tranformation function to the coordinate list of the
        # geometry
        transform_coords = lambda geom: projection_func(*zip(*geom.coords))

        # First we try to apply func to x, y, z sequences. When func is
        # optimized for sequences, this is the fastest, though zipping
        # the results up to go back into the geometry constructors adds
        # extra cost.
        try:
            if geom.type in ('Point', 'LineString'):
                return type(geom)(list(zip(*transform_coords(geom))))
            elif geom.type == 'Polygon':
                shell = type(geom.exterior)(
                    list(zip(*transform_coords(geom.exterior))))
                holes = list(
                    type(ring)(list(zip(*transform_coords(ring))))
                               for ring in geom.interiors)
                return type(geom)(shell, holes)

        # A func that assumes x, y, z are single values will likely raise a
        # TypeError, in which case we'll try again.
        except TypeError:
            ## Rather than applying f to the list, apply it individually
            ## to each coordinate
            transform_coords = lambda geom: list(starmap(projection_func, geom.coords))

            if geom.type in ('Point', 'LineString'):
                return type(geom)(transform_coords(geom))
            elif geom.type == 'Polygon':
                shell = type(geom.exterior)(transform_coords(geom.exterior))
                if not geom.interiors:
                    holes = []
                else:
                    ring_type = type(next(geom.interiors))
                    holes = list(type(ring_type)(
                            [transform_coords(ring) for ring in geom.interiors]))
                return type(geom)(shell, holes)

    elif geom.type.startswith('Multi'):
        coords = [
            project(part, from_proj, to_proj)
            for part in geom.geoms
            # if isinstance(part, sg.polygon.Polygon)
        ]
        return type(geom)(coords)
    elif isinstance(geom, sg.collection.GeometryCollection):
        # GeometryCollection can't be instantiated with data
        # must add data iteratively
        gc = sg.collection.GeometryCollection()
        for part in geom.geoms:
            gc = gc.union(project(part, from_proj, to_proj))
        return gc
    else:
        raise ValueError('Type {} not recognized'.format(geom.type))
