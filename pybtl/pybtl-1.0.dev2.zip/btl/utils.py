"""
This module contains lower-level functions for converting values to binary
format and vice versa.

.. note::
    The :py:class:`bitarray.bitarray` instances passed to and returned from the
    functions in this module, are expected to be big-endian.
"""

import struct

from bitarray import bitarray


LONG_LONG_BITS = 64


def int_to_bita(n):
    """
    Return a bitarray instance representing the specified number. The number
    must be an usigned integer. The number must be in C long long range.

    The return value will contain 64 bits (size of long long).

    Example::

        >>> int_to_bita(12)[-8:]
        bitarray('00001100')

    """
    try:
        bstr = struct.pack('>Q', n)
    except struct.error:
        raise ValueError('{} is out of range'.format(n))
    b = bitarray()
    b.frombytes(bstr)
    return b


def bita_to_int(b):
    """
    Return an integer that corresponds to the specified bitarray. The bitarray
    must represent a number that falls in the C long long range. Any
    significant bits beyond the 64 bits required to build a long long will be
    stripped away, and additional bits will be padded as needed to match the 64
    bit length.

    Example::

        >>> bita_to_int(bitarray('1100'))
        12

    """
    bits = b.to01().zfill(LONG_LONG_BITS)[-LONG_LONG_BITS:]
    bstr = bitarray(bits).tobytes()
    return struct.unpack('>Q', bstr)[0]


def bytes_to_bita(s):
    """
    Return a bitarray instance representing the bytestring. There is no limit
    to the length of the input.

    .. note::
        This function does exactly the same thing as packing bits into a
        :py:class:`~bitarray.bitarray` object using the
        :py:meth:`~bitarray.bitarray.frombytes` method.

    Example::

        >>> bytes_to_bita('foo')
        bitarray('011001100110111101101111')

    """
    b = bitarray()
    b.frombytes(s)
    return b


def bita_to_bytes(b):
    """
    Return a bytestring that is represented by the specified bitarray
    instance.

    .. note::
        This function does exactly the same thing as calling the
        :py:meth:`~bitarray.bitarray.tobytes` method.

    Example::

        >>> ba = bitarray('011001100110111101101111')
        >>> bita_to_bytes(ba)
        'foo'

    """
    return b.tobytes()


def str_to_bita(s):
    """
    Return a bitarray instance representing the specified string. The input can
    be a unicode string or a bytestring. Unicode strings will be encoded as
    UTF-8.


    Example::

        >>> str_to_bita(u'foo')
        bitarray('011001100110111101101111')

    """
    if not isinstance(s, bytes):
        s = s.encode('utf8')
    return bytes_to_bita(s)


def bita_to_str(b):
    """
    Return a string represented by the specified bitarray instance. The output
    is a unicode string. It is assumed that the input represents a
    UTF-8-encoded bytestring.

    Example::

        >>> bita = bitarray('011001100110111101101111')
        >>> bita_to_str(bita)
        u'foo'

    """
    bstr = bita_to_bytes(b)
    return bstr.decode('utf8')


def hex_digit_to_bita(h):
    """
    Return a 4-bit bitearray instance that represents a single hex digit.

    Example::

        >>> hex_digit_to_bita('a')
        bitarray('1010')
    """
    return int_to_bita(int(h, 16))[-4:]


def hex_to_bita(h):
    """
    Return a bitarray instance representing the hex number in the input
    string. There is no limit to the length of the input.

    Example::

        >>> hex_to_bita('f12a')
        bitarray('1111000100101010')

    """
    return sum([hex_digit_to_bita(d) for d in h], bitarray())


def bita_to_hex(b):
    """
    Return a hex number represented by the specified bitarray instance.

    Example::

        >>> bita_to_hex(bitarray('1111000100101010'))
        'f12a'

    """
    h = ''
    for i in range(0, len(b), 4):
        digit = b[i:i+4]
        h += hex(bita_to_int(digit))[-1]
    return h


def bool_to_bita(b):
    """
    Return a bitarray instance representing the boolean value.

    Example::

        >>> bool_to_bita(True)
        bitarray('1')

    """
    return bitarray([bool(b)])


def bita_to_bool(b):
    """
    Return a boolean value represented by the specified bitarray instance.

    Example::

        >>> bita_to_bool(bitarray('0'))
        False

    """
    return b[-1]  # only return last to account for longer bitarrays
