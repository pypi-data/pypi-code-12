"""structio - a more readable / convenient way to read data from streams"""
from enum import Enum
import struct

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO


class Endian(Enum):
    NATIVE_ALIGNED = '@'
    NATIVE = '='
    LITTLE = '<'
    BIG = '>'
    NETWORK = '!'


class CType(Enum):
    UINT8 = ('B', 1)
    INT8 = ('b', 1)
    UINT16 = ('H', 2)
    INT16 = ('h', 2)
    UINT32 = ('I', 4)
    INT32 = ('i', 4)
    UINT64 = ('Q', 8)
    INT64 = ('q', 8)
    FLOAT = ('f', 4)
    DOUBLE = ('d', 8)


class StructIO(BytesIO):
    _endian = Endian.NATIVE

    def set_endian(self, endian):
        """Set the endianness for struct-based reads on this stream"""
        self._endian = Endian(endian)

    def rewind(self, nbytes):
        """Rewind the stream by `nbytes`"""
        self.seek(-nbytes, 1)

    def forward(self, nbytes):
        self.seek(nbytes, 1)

    def peek(self, nbytes=1):
        """Peek ahead into the stream, returning `nbytes` (default 1)"""
        v = self.read(nbytes)
        self.rewind(len(v))
        return v

    def eof(self):
        return self.peek(1) == ''

    def copy(self, nbytes, offs=0, rel=1):
        """Returns a copy of this StructIO position, containing `nbytes`

        optional `offs`et and `rel` to be passed to seek() in case you want
        to make a copy of some data elsewhere in the stream (e.g., like substr)
        """
        original_pos = self.tell()
        self.seek(offs, rel)
        result = self.__class__(self.read(nbytes))
        self.seek(original_pos)
        return result

    def read_ctype(self, ctype):
        """Reads and returns the given `ctype` from the stream"""
        ctype = CType(ctype)
        exlen = ctype.value[1]
        buf = self.read(exlen)
        if len(buf) != exlen:
            raise EOFError("Expected %d bytes, got %d" % (exlen, len(buf)))
        v, = struct.unpack(self._endian.value + ctype.value[0], buf)
        return v

    def peek_ctype(self, ctype):
        """Reads and returns the given `ctype` from the stream

        Does not update the internal read pointer."""
        ctype = CType(ctype)
        v = self.read_ctype(ctype)
        self.rewind(ctype.value[1])
        return v

    def write_ctype(self, ctype, value):
        """Reads `value` as the specified the `ctype` into the stream"""
        ctype = CType(ctype)
        buf = struct.pack(self._endian.value + ctype.value[0], value)
        return self.write(buf)

    def read_uint8(self):
        """Extracts an 8-bit unsigned integer from the stream"""
        return self.read_ctype(CType.UINT8)
    def read_uint16(self):
        """Extracts a 16-bit unsigned integer from the stream"""
        return self.read_ctype(CType.UINT16)
    def read_uint32(self):
        """Extracts a 32-bit unsigned integer from the stream"""
        return self.read_ctype(CType.UINT32)
    def read_uint64(self):
        """Extracts a 64-bit unsigned integer from the stream"""
        return self.read_ctype(CType.UINT64)
    def read_int8(self):
        """Extracts an 8-bit signed integer from the stream"""
        return self.read_ctype(CType.INT8)
    def read_int16(self):
        """Extracts a 16-bit signed integer from the stream"""
        return self.read_ctype(CType.INT16)
    def read_int32(self):
        """Extracts a 32-bit signed integer from the stream"""
        return self.read_ctype(CType.INT32)
    def read_int64(self):
        """Extracts a 64-bit signed integer from the stream"""
        return self.read_ctype(CType.INT64)
    def read_float(self):
        """Extracts a 64-bit floating point number from the stream"""
        return self.read_ctype(CType.FLOAT)
    def read_double(self):
        """Extracts a 64-bit double precision number from the stream"""
        return self.read_ctype(CType.DOUBLE)

    def peek_uint8(self):
        return self.peek_ctype(CType.UINT8)
    def peek_uint16(self):
        return self.peek_ctype(CType.UINT16)
    def peek_uint32(self):
        return self.peek_ctype(CType.UINT32)
    def peek_uint64(self):
        return self.peek_ctype(CType.UINT64)
    def peek_int8(self):
        return self.peek_ctype(CType.INT8)
    def peek_int16(self):
        return self.peek_ctype(CType.INT16)
    def peek_int32(self):
        return self.peek_ctype(CType.INT32)
    def peek_int64(self):
        return self.peek_ctype(CType.INT64)
    def peek_float(self):
        return self.peek_ctype(CType.FLOAT)
    def peek_double(self):
        return self.peek_ctype(CType.DOUBLE)

    def write_uint8(self, value):
        return self.write_ctype(CType.UINT8, value)
    def write_uint16(self, value):
        return self.write_ctype(CType.UINT16, value)
    def write_uint32(self, value):
        return self.write_ctype(CType.UINT32, value)
    def write_uint64(self, value):
        return self.write_ctype(CType.UINT64, value)
    def write_int8(self, value):
        return self.write_ctype(CType.INT8, value)
    def write_int16(self, value):
        return self.write_ctype(CType.INT16, value)
    def write_int32(self, value):
        return self.write_ctype(CType.INT32, value)
    def write_int64(self, value):
        return self.write_ctype(CType.INT64, value)
    def write_float(self, value):
        return self.write_ctype(CType.FLOAT, value)
    def write_double(self, value):
        return self.write_ctype(CType.DOUBLE, value)
