from __future__ import division, absolute_import, print_function
from struct import unpack, error
from traceback import print_exc

from more_itertools import chunked


def unpack_int(stream, fmt, width, callback):
    """Interpret the stream as integers."""
    for one in chunked(stream.read(), int(width) // 8):
        try:
            # TODO: Support Python 2.
            item = callback(unpack(fmt, bytes(one))[0])
        except error:
            print_exc()
        else:
            yield item
