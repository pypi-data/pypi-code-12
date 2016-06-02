"""Module to test PyGeoprocessing module."""
import unittest

from osgeo import gdal
import numpy


class PyGeoprocessingTest(unittest.TestCase):
    """Class to test PyGeoprocessing's functions."""

    def test_map_dataset_to_value(self):
        """Test map_dataset_to_value if raster is missing a nodata value."""
        import pygeoprocessing

        n_rows, n_cols = 4, 4
        driver = gdal.GetDriverByName('GTiff')
        raster_path = 'test.tif'
        new_raster = driver.Create(
            raster_path, n_cols, n_rows, 1, gdal.GDT_Int32)
        band = new_raster.GetRasterBand(1)
        band.WriteArray(numpy.ones((n_rows, n_cols), dtype=numpy.int32))

        out_nodata = -1.0
        value_map = {1: 100.0}
        raster_out_path = 'test_out.tif'
        pygeoprocessing.reclassify_dataset_uri(
            raster_path, value_map, raster_out_path, gdal.GDT_Float64,
            out_nodata)

        raster_out = gdal.Open(raster_out_path)
        raster_out_band = raster_out.GetRasterBand(1)
        self.assertEqual(numpy.unique(raster_out_band.ReadAsArray), 100.0)
