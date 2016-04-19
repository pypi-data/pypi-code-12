import sys
from io import BytesIO
try:
    from cPickle import Pickler, Unpickler, HIGHEST_PROTOCOL
except:
    from pickle import Pickler, Unpickler, HIGHEST_PROTOCOL


class Pickle():

    def dumps(self, obj, protocol=HIGHEST_PROTOCOL):
        file = BytesIO()
        Pickler(file, protocol).dump(obj)
        return file.getvalue()

    def loads(self, str):
        file = BytesIO(str)
        return Unpickler(file).load()


def load_module(path, filename):
    filename = filename.strip('.py')
    sys.path.insert(0, path)
    module = __import__(filename)
    del sys.path[0]
    return module
