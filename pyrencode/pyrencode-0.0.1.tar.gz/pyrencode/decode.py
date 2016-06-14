import struct

from pyrencode.settings import *

_decode_utf8 = DECODE_UTF8


def decode_int(bytes_obj, cursor):
    cursor += 1
    new_cursor = bytes_obj.index(CHR_TERM, cursor)
    if new_cursor - cursor >= MAX_INT_LENGTH:
        raise ValueError('overflow')
    n = int(bytes_obj[cursor:new_cursor])
    if bytes_obj[cursor:cursor + 1] == '-':
        if bytes_obj[cursor + 1:cursor + 2] == '0':
            raise ValueError
    elif bytes_obj[cursor:cursor + 1] == '0' and new_cursor != cursor + 1:
        raise ValueError

    return n, new_cursor + 1


def decode_int1(bytes_obj, cursor):
    cursor += 1
    return struct.unpack('!b', bytes_obj[cursor:cursor + 1])[0], cursor + 1


def decode_int2(bytes_obj, cursor):
    cursor += 1
    return struct.unpack('!h', bytes_obj[cursor:cursor + 2])[0], cursor + 2


def decode_int3(bytes_obj, cursor):
    cursor += 1
    return struct.unpack('!l', bytes_obj[cursor:cursor + 4])[0], cursor + 4


def decode_int4(bytes_obj, cursor):
    cursor += 1
    return struct.unpack('!q', bytes_obj[cursor:cursor + 8])[0], cursor + 8


def decode_float32(bytes_obj, cursor):
    cursor += 1
    return struct.unpack('!f', bytes_obj[cursor:cursor + 4])[0], cursor + 4


def decode_float64(bytes_obj, cursor):
    cursor += 1
    return struct.unpack('!d', bytes_obj[cursor:cursor + 8])[0], cursor + 8


def decode_string(bytes_obj, cursor):
    colon = bytes_obj.index(b':', cursor)
    n = int(bytes_obj[cursor:colon])
    if bytes_obj[cursor] == '0' and colon != cursor + 1:
        raise ValueError
    colon += 1
    string = bytes_obj[colon:colon + n]
    if _decode_utf8:
        string = string.decode('utf8')
    return string, colon + n


def decode_list(bytes_obj, cursor):
    r, cursor = [], cursor + 1
    while bytes_obj[cursor:cursor + 1] != CHR_TERM:
        v, cursor = decode_func[bytes_obj[cursor:cursor + 1]](
            bytes_obj,
            cursor,
        )
        r.append(v)
    return tuple(r), cursor + 1


def decode_dict(x, cursor):
    r, cursor = {}, cursor + 1
    while x[cursor:cursor + 1] != CHR_TERM:
        k, cursor = decode_func[x[cursor:cursor + 1]](x, cursor)
        r[k], cursor = decode_func[x[cursor:cursor + 1]](x, cursor)
    return r, cursor + 1


def decode_true(_, cursor):
    return True, cursor + 1


def decode_false(_, cursor):
    return False, cursor + 1


def decode_none(_, cursor):
    return None, cursor + 1


decode_func = {
    b'0': decode_string,
    b'1': decode_string,
    b'2': decode_string,
    b'3': decode_string,
    b'4': decode_string,
    b'5': decode_string,
    b'6': decode_string,
    b'7': decode_string,
    b'8': decode_string,
    b'9': decode_string,
    CHR_LIST: decode_list,
    CHR_DICT: decode_dict,
    CHR_INT: decode_int,
    CHR_INT1: decode_int1,
    CHR_INT2: decode_int2,
    CHR_INT4: decode_int3,
    CHR_INT8: decode_int4,
    CHR_FLOAT32: decode_float32,
    CHR_FLOAT64: decode_float64,
    CHR_TRUE: decode_true,
    CHR_FALSE: decode_false,
    CHR_NONE: decode_none,
}


def make_fixed_length_string_decoders():
    def make_decoder(slen):
        def func(x, f):
            s = x[f + 1:f + 1 + slen]
            if _decode_utf8:
                s = s.decode("utf8")
            return s, f + 1 + slen

        return func

    for i in range(STR_FIXED_COUNT):
        decode_func[int2byte(STR_FIXED_START + i)] = make_decoder(i)


make_fixed_length_string_decoders()


def make_fixed_length_list_decoders():
    def make_decoder(slen):
        def func(x, f):
            r, f = [], f + 1
            for _ in range(slen):
                v, f = decode_func[x[f:f + 1]](x, f)
                r.append(v)
            return tuple(r), f

        return func

    for i in range(LIST_FIXED_COUNT):
        decode_func[int2byte(LIST_FIXED_START + i)] = make_decoder(i)


make_fixed_length_list_decoders()


def make_fixed_length_int_decoders():
    def make_decoder(j):
        def func(_, f):
            return j, f + 1

        return func

    for i in range(INT_POS_FIXED_COUNT):
        decode_func[int2byte(INT_POS_FIXED_START + i)] = make_decoder(i)
    for i in range(INT_NEG_FIXED_COUNT):
        decode_func[int2byte(INT_NEG_FIXED_START + i)] = make_decoder(-1 - i)


make_fixed_length_int_decoders()


def make_fixed_length_dict_decoders():
    def make_decoder(slen):
        def func(x, f):
            r, f = {}, f + 1
            for _ in range(slen):
                k, f = decode_func[x[f:f + 1]](x, f)
                r[k], f = decode_func[x[f:f + 1]](x, f)
            return r, f

        return func

    for i in range(DICT_FIXED_COUNT):
        decode_func[int2byte(DICT_FIXED_START + i)] = make_decoder(i)


make_fixed_length_dict_decoders()


def loads(bytes_obj, decode_utf8=False):
    global _decode_utf8
    _decode_utf8 = decode_utf8
    try:
        obj, end_position = decode_func[bytes_obj[0:1]](bytes_obj, 0)
    except (IndexError, KeyError):
        raise ValueError
    if end_position != len(bytes_obj):
        raise ValueError
    return obj
