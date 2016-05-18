"""
    stringint
    ~~~~~~~~~

    :copyright: 2016 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import sys


__version__ = '0.1.0'
__version_info__ = (0, 1, 0)


BYTES = 256
CODEPOINTS = sys.maxunicode + 1


def bytes_to_int(bytes):
    """
    Takes a byte string and returns an unsigned int.
    """
    result = 1
    for byte in bytes:
        result = result * BYTES + byte
    return result


def int_to_bytes(int):
    """
    Takes an unsigned int as returned by `bytes_to_int` and turns it into a
    byte string again.
    """
    result = bytearray()
    while int > 1:
        int, byte = divmod(int, BYTES)
        result.append(byte)
    return bytes(result[::-1])


def string_to_int(string):
    """
    Takes a string and returns an unsigned int.
    """
    result = 1
    for codepoint in string:
        result = result * CODEPOINTS + ord(codepoint)
    return result


def int_to_string(int):
    """
    Takes an unsigned int as returned by `string_to_int` and turns it into a
    string again.
    """
    result = []
    while int > 1:
        int, codepoint = divmod(int, CODEPOINTS)
        result.append(chr(codepoint))
    return ''.join(reversed(result))
