
import json, os, shutil, tempfile
from bf.file import File
from bl.dict import Dict

class JSON(File):

    def __init__(self, fn=None, data=None, **args):
        File.__init__(self, fn=fn, **args)
        if data is not None:
            self.data = data
        elif self.fn is not None and os.path.exists(self.fn):
            self.data = self.read()
        if type(self.data)==dict:
            self.data = Dict(**self.data)

    def read(self):
        d = File.read(self, mode='r')
        j = json.loads(d)
        return j

    def write(self, fn=None, data=None, indent=2, **args):
        File.write(self, 
            fn=fn or self.fn, 
            data=json.dumps(data or self.data, indent=indent).encode('utf-8'), 
            **args)
        
