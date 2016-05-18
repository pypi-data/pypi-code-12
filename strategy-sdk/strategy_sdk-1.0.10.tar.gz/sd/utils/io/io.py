# encoding: utf-8
from __future__ import absolute_import
import io
import struct

try:
    import errno
except ImportError:
    errno = None

__author__ = u'Yonka'

EBADF = getattr(errno, 'EBADF', 9)
EAGAIN = getattr(errno, 'EAGAIN', 11)
EWOULDBLOCK = getattr(errno, 'EWOULDBLOCK', 11)

_blocking_errnos = {EAGAIN, EWOULDBLOCK}


class timeout(OSError):
    # no doc
    def __init__(self, *args, **kwargs):  # real signature unknown
        pass

    __weakref__ = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """list of weak references to the object (if defined)"""


class error(Exception):
    """ Base class for I/O related errors. """

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass

    @staticmethod  # known case of __new__
    def __new__(*args, **kwargs):  # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        pass

    def __reduce__(self, *args, **kwargs):  # real signature unknown
        pass

    def __str__(self, *args, **kwargs):  # real signature unknown
        """ Return str(self). """
        pass

    characters_written = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default

    errno = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """POSIX exception code"""

    filename = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """exception filename"""

    filename2 = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """second exception filename"""

    strerror = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """exception strerror"""

    winerror = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """Win32 exception code"""


class SocketIO(io.RawIOBase):
    """Raw I/O implementation for stream sockets.

    This class supports the makefile() method on sockets.  It provides
    the raw I/O interface on top of a socket object.
    """

    # One might wonder why not let FileIO do the job instead.  There are two
    # main reasons why FileIO is not adapted:
    # - it wouldn't work under Windows (where you can't used read() and
    # write() on a socket handle)
    # - it wouldn't work with socket timeouts (FileIO would ignore the
    # timeout and consider the socket non-blocking)

    # XXX More docs

    def __init__(self, sock, mode):
        if mode not in ("r", "w", "rw", "rb", "wb", "rwb"):
            raise ValueError("invalid mode: %r" % mode)
        io.RawIOBase.__init__(self)
        self._sock = sock
        if "b" not in mode:
            mode += "b"
        self._mode = mode
        self._reading = "r" in mode
        self._writing = "w" in mode
        self._timeout_occurred = False

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.

        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        while True:
            try:
                return self._sock.recv_into(b)
            except timeout:
                self._timeout_occurred = True
                raise
            except error as e:
                if e.args[0] in _blocking_errnos:
                    return None
                raise

    def write(self, b):
        """Write the given bytes or bytearray object *b* to the socket
        and return the number of bytes written.  This can be less than
        len(b) if not all data could be written.  If the socket is
        non-blocking and no bytes could be written None is returned.
        """
        self._checkClosed()
        self._checkWritable()
        try:
            return self._sock.send(b)
        except error as e:
            # XXX what about EINTR?
            if e.args[0] in _blocking_errnos:
                return None
            raise

    def readable(self):
        """True if the SocketIO is open for reading.
        """
        if self.closed:
            raise ValueError("I/O operation on closed socket.")
        return self._reading

    def writable(self):
        """True if the SocketIO is open for writing.
        """
        if self.closed:
            raise ValueError("I/O operation on closed socket.")
        return self._writing

    def seekable(self):
        """True if the SocketIO is open for seeking.
        """
        if self.closed:
            raise ValueError("I/O operation on closed socket.")
        return super(SocketIO, self).seekable()

    def fileno(self):
        """Return the file descriptor of the underlying socket.
        """
        self._checkClosed()
        return self._sock.fileno()

    @property
    def name(self):
        if not self.closed:
            return self.fileno()
        else:
            return -1

    @property
    def mode(self):
        return self._mode

    def close(self):
        """Close the SocketIO object.  This doesn't close the underlying
        socket, except if all references to it have disappeared.
        """
        if self.closed:
            return
        io.RawIOBase.close(self)
        self._sock._decref_socketios()
        self._sock = None


class DataStream(object):
    def __init__(self, base_stream, endian=""):
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
        return self.unpack(unicode(length) + u's', length)  # endian seems to do not affect this...

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
        self.pack(unicode(length) + 's', value)

    def pack(self, fmt, data):
        return self.write_bytes(struct.pack(fmt, data))
