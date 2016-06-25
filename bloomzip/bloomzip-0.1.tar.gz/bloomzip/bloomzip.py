from pybloom import BloomFilter
from gzip import GzipFile
from six import StringIO
import struct
import os
import tempfile


class BloomZip(object):
    def __init__(self, name):
        super(BloomZip, self).__init__()
        self.__data = StringIO()
        self._name = name
        self._bf = None

        if os.path.isfile(self._name):
            with open(self._name, 'rb') as f:
                length = struct.unpack(">L", f.read(4))[0]
                self._bf = BloomFilter.fromfile(f, length)

    def contains(self, word):
        return word in self._bf

    def write(self, data):
        self.__data.write(data)

    def close(self):
        if self._bf is None and self.__data is None:
            return

        words = self.__data.getvalue().split()

        self._bf = BloomFilter(capacity=len(words) + 1)

        for word in words:
            self._bf.add(word, skip_check=True)

        def get_bl_size():
            t = tempfile.NamedTemporaryFile().name
            with open(t, 'w') as fn:
                self._bf.tofile(fn)
            s = os.path.getsize(t)
            os.remove(t)
            return s

        if os.path.isfile(self._name):
            return

        a = open(self._name, 'w')
        a.write(struct.pack(">L", get_bl_size()))
        self._bf.tofile(a)
        with GzipFile(self._name, 'w', fileobj=a) as f:
            f.write(self.__data.getvalue())
        a.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        if exc_type is not None:
            print(exc_tb)
            raise exc_val
