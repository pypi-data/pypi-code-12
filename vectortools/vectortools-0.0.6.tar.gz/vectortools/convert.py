import os
import tempfile
from osgeo import ogr
from .fsutils import TempDir
from .reader import VectorReader

class VectorWriterError(Exception):
    pass

class Converter(object):
    def __init__(self, output_format):
        self.output_driver = ogr.GetDriverByName(output_format)
        if not self.output_driver:
            raise VectorWriterError('invalid output format')
        
    def convert_ds(self, source_ds, output_filename, layer_to_copy=None):
        tmp_dir = tempfile.mkdtemp()
        output_path = os.path.join(tmp_dir, output_filename)
        if layer_to_copy is None:
            output_ds = self.output_driver.CopyDataSource(source_ds, output_path)
        else:
            output_ds = self.output_driver.CreateDataSource(output_path)
            layer = source_ds.GetLayer(layer_to_copy)
            output_ds.CopyLayer(layer, layer.GetName())
        output_ds.Destroy()
        return TempDir(tmp_dir)
    
    def convert_file(self, filepath, output_filename, layer_to_copy=None):
        vr = VectorReader(filepath)
        return self.convert_ds(vr.ds, output_filename, layer_to_copy)
