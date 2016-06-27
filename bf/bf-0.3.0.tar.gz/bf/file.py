
import os, subprocess, time
from bl.dict import Dict
from bl.log import Log

class File(Dict):
    def __init__(self, fn=None, data=None, log=Log(), **args):
        if type(fn)==str: fn=fn.strip().replace('\\ ', ' ')
        Dict.__init__(self, fn=fn, data=data, log=log, **args)

    def __repr__(self):
        return "%s(fn=%r)" % (
            self.__class__.__name__, self.fn)

    @classmethod
    def readable_size(C, size, suffix='B'):
        if size is None: return
        size = float(size)
        for unit in ['','K','M','G','T','P','E','Z']:
            if abs(size) < 1024.0:
                return "%3.1f %s%s" % (size, unit, suffix)
            size /= 1024.0
        return "%.1f %s%s" % (size, 'Y', suffix)

    def open(self):
        subprocess.call(['open', fn], shell=True)

    def read(self, mode='rb'):
        with open(self.fn, mode) as f:
            data = f.read()
        return data

    def dirpath(self):
        return os.path.dirname(os.path.abspath(self.fn))

    def basename(self):
        return os.path.basename(self.fn)

    def ext(self):
        return os.path.splitext(self.fn)[1]

    def relpath(self, dirpath=None):
        return os.path.relpath(self.fn, dirpath or self.dirpath()).replace('\\','/')

    def mimetype(self):
        from mimetypes import guess_type
        return guess_type(self.fn)[0]

    def tempfile(self, mode='wb', **args):
        "write the contents of the file to a tempfile and return the tempfile filename"
        tf = tempfile.NamedTemporaryFile(mode=mode)
        self.write(tf.name, mode=mode, **args)
        return tfn

    def write(self, fn=None, data=None, mode='wb', 
                max_tries=3):                   # sometimes there's a disk error on SSD, so try 3x
        outfn = fn or self.fn
        if not os.path.exists(os.path.dirname(outfn)):
            os.makedirs(os.path.dirname(outfn))
        def try_write(fd=None, tries=0):         
            try:
                if fd is None:
                    if 'fd' in mode:
                        fd=self.read(mode='rb')
                    else:
                        fd=self.read(mode='r')
                f = open(outfn, mode)
                f.write(fd)
                f.close()
            except: 
                if tries < max_tries:
                    time.sleep(.1)              # I found 0.1 s gives the disk time to recover. YMMV
                    try_write(tries=tries+1)
                else:
                    raise
        try_write(fd=data or self.data, tries=0)
