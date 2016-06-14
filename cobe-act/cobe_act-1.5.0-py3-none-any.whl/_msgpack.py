"""Simple wrappers around msgpack.

Since msgpack evolved a rather awkward API in order to handle unicode
in a backwards compatible way this module provides some simple
wrappers to correctly use the msgpack API.

"""

import msgpack


def mpack(data):
    """Encode Python data to a msgpack object.

    This will always use the bin type feature, encoding unicode
    strings as UTF-8.  This uses the :func:`msgpack.packb` API which
    means the entire object will be loaded into memory.

    :param data: The data to encode in msgpack.
    :type data: Any Python object which can be encoded to msgpack.

    :returns: A bytestring containing the encoded data.

    """
    return msgpack.packb(data, use_bin_type=True)


def munpack(data):
    """Decode the msgpack-encoded data into a Python object.

    This assumes that any strings in the encoded data are encoded
    using the UTF-8 codec, and is thus the inverse of :func:`mpack`.
    This uses the :func:`msgpack.unpackb` API which means the entire
    object will be loaded into memory.

    :param bytes data: The msgpack-encoded data.

    :returns: A Python object.

    """
    return msgpack.unpackb(data, encoding='utf-8')
