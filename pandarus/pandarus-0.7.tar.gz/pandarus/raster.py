# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from eight import *
from future.utils import python_2_unicode_compatible

from osgeo import ogr, gdal, osr
from osgeo.gdalconst import GDT_Float32
from shapely.wkt import loads
import os


@python_2_unicode_compatible
class Raster(object):
    """Nicer wrapper around GDAL functionality"""
    def __init__(self, filepath, band=1, loc_cache=True):
        """Load raster file"""
        assert os.path.exists(filepath), "Can't load file {}".format(filepath)
        self.filepath = filepath
        self.raster = gdal.Open(filepath)
        self.band_n = band
        self.info()
        if loc_cache:
            self.loc_cache = self.create_loc_cache()

    def _(self, band):
        if isinstance(band, int):
            return band
        else:
            return self.band_n

    def create_loc_cache(self):
        no_data = self.no_data_value()
        array = self.array()
        data = [
            (row, col)
            for col in range(self.nx)
            for row in range(self.ny)
            if array[row, col] != no_data
        ]
        return {index: obj for index, obj in enumerate(data)}

    def __repr__(self):
        fmt = "Raster(extent=({:.4e}, {:.4e}, {:.4e}, {:.4e})"
        fmt += ", pixel=({}, {}), gridsize=({}, {}))"
        return fmt.format(self.left, self.bottom, self.right, self.top,
                      self.xsize, self.ysize, self.nx, self.ny)

    def _label(self, x, y):
        return 'Cell({:.8e}, {:.8e})'.format(x, y)

    def __getitem__(self, index):
        if hasattr(self, "loc_cache"):
            if not isinstance(index, int):
                raise ValueError("Item index must be integer")
            row, col = self.loc_cache[index]
            wkt = self.wkt_for_coords(col, row)
            shape = loads(wkt)
            return {
                'geometry': wkt,
                'label': self._label(shape.centroid.x, shape.centroid.y),
                'row': row,
                'col': col,
                'value': float(self.array()[row, col]),
            }
        else:
            raise NotImplemented

    def __iter__(self):
        """Create generator that iterates over raster cells with real values.

        For each cell, return the following data structure:

        .. code-block:: python

            {
                'geometry': WKT for this raster cell geometry,
                'label': String of form "Cell(x, y)", where x and y are longitude and latitude of the raster cell centroid,
                'row': Integer row index into raster array,
                'col': Integer column index into raster array
            }
        """
        no_data = self.no_data_value()
        array = self.array()
        for col in range(self.nx):
            for row in range(self.ny):
                if array[row, col] == no_data:
                    continue
                wkt = self.wkt_for_coords(col, row)
                shape = loads(wkt)
                yield {
                    'geometry': wkt,
                    'label': self._label(shape.centroid.x, shape.centroid.y),
                    'row': row,
                    'col': col,
                    'value': float(array[row, col]),
                }

    def __len__(self):
        """Return number of raster cells with real values (no NODATA)"""
        return int((self.array() != self.no_data_value()).sum())

    @property
    def crs(self):
        """Use OSR to get coordinate reference system as PROJ.4 string"""
        geogcs = self.raster.GetProjection()
        sr = osr.SpatialReference()
        sr.ImportFromWkt(geogcs)
        return sr.ExportToProj4()

    def info(self):
        """Set raster geotransform data. Doesn't return anything"""
        t = self.raster.GetGeoTransform()
        self.left  = t[0]
        self.xsize = t[1]
        self.top   = t[3]
        self.ysize = t[5]

        self.nx = self.raster.RasterXSize
        self.ny = self.raster.RasterYSize

        self.bottom = self.top  + self.ysize * self.ny
        self.right  = self.left + self.xsize * self.nx

        assert self.right > self.left, "bounds are messed up"
        if self.bottom > self.top:
            self.bottom, self.top = self.top, self.bottom
            self.ysize *= -1

    @property
    def extent(self):
        return (self.left, self.bottom, self.right, self.top)

    def array(self, band=None):
        """Return raster data as NumPy array"""
        return self.band(band).ReadAsArray()

    def band(self, band=None):
        """Get GDAL `Band` object"""
        return self.raster.GetRasterBand(self._(band))

    def no_data_value(self, band=None):
        return self.band(band).GetNoDataValue()

    def get_writer(self, filepath):
        """Get TIFF GDAL writer with projection and geotransform of current raster.

        Assumes 1-band raster with 32 bit floating point number."""
        driver = gdal.GetDriverByName('GTiff')
        out = driver.Create(filepath, self.nx, self.ny, 1, GDT_Float32, [])
        out.SetProjection(self.raster.GetProjection())
        out.SetGeoTransform(self.raster.GetGeoTransform())
        return out

    def write_modified_array(self, filepath, array, options=[],
            nodata=None, band=None):
        """Write NumPy array `array` to `filepath`"""
        out = self.get_writer(filepath)
        new_band = out.GetRasterBand(self._(band))
        if nodata:
            new_band.SetNoDataValue(float(nodata))
        new_band.WriteArray(array)
        new_band.FlushCache()
        new_band = None
        out = None

    def wkt_for_coords(self, x, y, rounded=False):
        """Get WKT for column `x` and row `y` (integer indices).

        `rounded` rounds to 5 decimal places."""
        POLYGON_TEMPLATE = "POLYGON(({:g} {:g},{:g} {:g},{:g} {:g},{:g} {:g},{:g} {:g}))"
        if rounded:
            POLYGON_TEMPLATE = ("POLYGON(({:.5f} {:.5f},{:.5f} {:.5f},{:.5f} "
                                "{:.5f},{:.5f} {:.5f},{:.5f} {:.5f}))")
        return POLYGON_TEMPLATE.format(
            self.left + x * self.xsize, # Lower left
            self.top + y * self.ysize,
            self.left + x * self.xsize, # Upper left
            self.top + (y + 1) * self.ysize,
            self.left + (x + 1) * self.xsize, # Upper right
            self.top + (y + 1) * self.ysize,
            self.left + (x + 1) * self.xsize, # Lower right
            self.top + y * self.ysize,
            self.left + x * self.xsize, # Lower left
            self.top + y * self.ysize,
            )
