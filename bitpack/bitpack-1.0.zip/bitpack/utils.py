import struct


def pack(fmt, raw_data):
    """Delegates calls to `struct.pack` without any intervention. Exists for
    the sole purpose to make the API nicer, by providing a twin to the
    ``bitpack.utils.unpack`` function, which performs not only delegation,
    but also some additional work.

    :param fmt:      struct format string
    :param raw_data: value to be packed
    """
    return struct.pack(fmt, raw_data)


def unpack(fmt, raw_bytes):
    """Left-pads the contents of ``raw_bytes`` with zero-bytes, so it's size
    matches the expected size of the type to which it's planned to be
    unpacked and passes the padded data to ``struct.unpack``, returning the
    result of that call.

    :param fmt:       struct format string
    :param raw_bytes: data to be unpacked
    """
    expected_size = struct.calcsize(fmt)
    while len(raw_bytes) < expected_size:
        raw_bytes = '\x00' + raw_bytes
    (value,) = struct.unpack(fmt, raw_bytes)
    return value


def hex_to_bytes(hs):
    """Convert an arbitary string containing only hexadecimal values to raw
    bytes, by converting each hexadecimal value-pair to their ascii symbol
    representation. The input string's length must be even to perform correct
    conversion. This requirement was introduced so that we can halve the size
    of the output byte array.

    :param hs: string of even length containing hexadecimal values only
    """
    if len(hs) % 2 != 0:
        raise ValueError("The input string's length is not even.")

    chunks = [hs[i:i + 2] for i in range(0, len(hs), 2)]
    return ''.join([chr(int(byte, 16)) for byte in chunks])


def bytes_to_hex(s):
    """Convert an arbitary string to it's hexadecimal representation, by
    converting each byte of the string to the hexadecimal value that the
    byte represents.

    :param s: string
    """
    return ''.join(['{:02x}'.format(ord(c)) for c in s])
