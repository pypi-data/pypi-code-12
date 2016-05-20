import os
import tempfile
import zipfile
import shutil
from osgeo import ogr

ogr.DontUseExceptions()
ogr.UseExceptions()

class VectorReaderError(Exception):
    pass

class VectorReaderBadZipFile(VectorReaderError):
    pass

class VectorReader(object):
    
    def __init__(self, filepath):
        self.temp_dirs = []
        if os.path.splitext(filepath)[1] == '.zip':
            try:
                filepath = self.extract_zip(filepath)
            except zipfile.BadZipfile:
                raise VectorReaderBadZipFile()
        try:
            #hack for old gdal versions, they throw errors on unicode string as filepath
            path = filepath.encode('utf-8') if isinstance(filepath, unicode) else filepath
            
            self.ds = ogr.Open(path)
        except RuntimeError:
            self.ds = None
        if not self.ds:
            raise VectorReaderError('file does not contains vector data or has invalid format')

    def extract_zip(self, filepath):
        temp_dir = tempfile.mkdtemp()
        zf = zipfile.ZipFile(filepath)
        zf.extractall(temp_dir)
        self.temp_dirs.append(temp_dir)
        return temp_dir

    def __len__(self):
        return self.ds.GetLayerCount()

    def __del__(self):
        for path in self.temp_dirs:
            shutil.rmtree(path)
