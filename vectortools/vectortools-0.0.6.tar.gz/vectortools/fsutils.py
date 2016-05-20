import os
import tempfile
import shutil
import zipfile

class TempDir(object):
    def __init__(self, path=None):
        self.path = path or tempfile.mkdtemp()
    
    def create_zip(self):
        tmp_file = tempfile.NamedTemporaryFile(suffix='.zip')
        zf = zipfile.ZipFile(tmp_file, 'w')
        for dirname, subdirs, files in os.walk(self.path):
            for filename in files:
                fullpath = os.path.join(dirname, filename)
                zf.write(fullpath, os.path.relpath(fullpath, self.path))
        zf.close()
        tmp_file.seek(0)
        return tmp_file
        
    def file_list(self):
        return [os.path.join(self.path, f) for f in os.listdir(self.path)]
        
    def __del__(self):
        shutil.rmtree(self.path)
