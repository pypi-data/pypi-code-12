
import os, sys, time
from bl.dict import Dict

class Log(Dict):
    """log file, which appends to the file rather than reading"""

    def __init__(self, fn=None, echo=False):
        super().__init__(fn=fn, echo=echo)

    def write(self, string):
        self.__call__(string, end='')

    def __call__(self, *args, sep=' ', end='\n'):
        f = self.open()
        print(*args, file=f, sep=sep, end=end)
        self.close(f)
        if self.echo==True: 
            print(*args, sep=sep, end=end)

    def open(self, fn=None):
        fn = fn or self.fn
        if fn is not None:
            if not os.path.exists(os.path.dirname(fn)):
                os.makedirs(os.path.dirname(fn))
            f = open(fn, 'a')
        else:
            f = sys.stdout
        return f 

    def close(self, f):
        if f != sys.stdout:
            f.close()

    def delete(self):
        if os.path.exists(self.fn):
            os.remove(self.fn)

    @classmethod
    def timestamp(C):
        return time.strftime("%Y-%m-%d %H:%M:%S %Z")

