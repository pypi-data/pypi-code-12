# zip.py - class for handling ZIP files

from zipfile import ZipFile, ZIP_DEFLATED
import os
from bl.dict import Dict
from bl.log import Log

class ZIP(Dict):
    """zipfile wrapper"""

    def __init__(self, fn=None, mode='r', compression=ZIP_DEFLATED, log=Log(), **args):
        Dict.__init__(self, fn=fn, mode=mode, compression=compression, log=log, **args)
        if fn is not None:
            self.zipfile = ZipFile(self.fn, mode=mode, compression=compression)

    def unzip(self, path=None, members=None, pwd=None):
        if path is None: path = os.path.splitext(self.fn)[0]
        if not os.path.exists(path): os.makedirs(path)
        self.zipfile.extractall(path=path, members=members, pwd=pwd)

    def close(self):
        self.zipfile.close()

    @classmethod
    def zip_path(CLASS, path, fn=None, mode='w', exclude=[], log=Log()):
        if fn is None:
            fn = path+'.zip'
        zipf = CLASS(fn, mode=mode).zipfile
        for walk_tuple in os.walk(path):
            dirfn = walk_tuple[0]
            for fp in walk_tuple[-1]:
                walkfn = os.path.join(dirfn, fp)
                if os.path.relpath(walkfn, path) not in exclude:
                    zipf.write(walkfn, os.path.relpath(walkfn, path))
        zipf.close()
        return fn
