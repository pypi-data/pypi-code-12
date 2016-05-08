# encoding: utf-8
from io import RawIOBase
import struct

__author__ = 'Yonka'


class DataStream(object):
    def __init__(self, base_stream: RawIOBase, endian: str=""):
        if endian is None:
            endian = ""
        self._endian = endian
        self.base_stream = base_stream
        self._char_fmt = 'b'
        self._unsigned_char_fmt = 'B'
        self._bool_fmt = '?'
        self._short_fmt = endian + 'h'
        self._unsigned_short_fmt = endian + 'H'
        self._int_fmt = endian + 'i'
        self._unsigned_int_fmt = endian + 'I'
        self._long_fmt = endian + 'l'
        self._unsigned_long_fmt = endian + 'L'
        self._long_long_fmt = endian + 'q'
        self._unsigned_long_long_fmt = endian + 'Q'
        self._float_fmt = endian + 'f'
        self._double_fmt = endian + 'd'
        self._chars_fmt = endian + 's'

    def read_byte(self):
        return self.base_stream.read(1)

    def read_bytes(self, length):
        bs = self.base_stream.read(length)
        if bs is None or len(bs) == 0:
            raise IOError("read_bytes(%d), but got bs %s" % (length, bs))
        return bs

    def read_char(self):
        return self.unpack(self._char_fmt)

    def read_uchar(self):
        return self.unpack(self._unsigned_char_fmt)

    def read_bool(self):
        return self.unpack(self._bool_fmt)

    def read_int16(self):
        return self.unpack(self._short_fmt, 2)

    def read_uint16(self):
        return self.unpack(self._unsigned_short_fmt, 2)

    def read_int32(self):
        return self.unpack(self._int_fmt, 4)

    def read_uint32(self):
        return self.unpack(self._unsigned_int_fmt, 4)

    def read_int64(self):
        return self.unpack(self._long_long_fmt, 8)

    def read_uint64(self):
        return self.unpack(self._unsigned_long_long_fmt, 8)

    def read_float(self):
        return self.unpack(self._float_fmt, 4)

    def read_double(self):
        return self.unpack(self._double_fmt, 8)

    def read_string(self):
        length = self.read_uint16()
        return self.unpack(str(length) + 's', length)  # endian seems to do not affect this...

    def unpack(self, fmt, length=1):
        bs = self.read_bytes(length)
        res = struct.unpack(fmt, bs)[0]
        return res

    def write_bytes(self, value):
        self.base_stream.write(value)

    def write_char(self, value):
        self.pack(self._char_fmt, value)

    def write_uchar(self, value):
        self.pack(self._unsigned_char_fmt, value)

    def write_bool(self, value):
        self.pack(self._bool_fmt, value)

    def write_int16(self, value):
        self.pack(self._short_fmt, value)

    def write_uint16(self, value):
        self.pack(self._unsigned_short_fmt, value)

    def write_int32(self, value):
        self.pack(self._int_fmt, value)

    def write_uint32(self, value):
        self.pack(self._unsigned_int_fmt, value)

    def write_int64(self, value):
        self.pack(self._long_long_fmt, value)

    def write_uint64(self, value):
        self.pack(self._unsigned_long_long_fmt, value)

    def write_float(self, value):
        self.pack(self._float_fmt, value)

    def write_double(self, value):
        self.pack(self._double_fmt, value)

    def write_string(self, value):
        length = len(value)
        self.write_uint16(length)
        self.pack(str(length) + 's', value)

    def pack(self, fmt, data):
        return self.write_bytes(struct.pack(fmt, data))
