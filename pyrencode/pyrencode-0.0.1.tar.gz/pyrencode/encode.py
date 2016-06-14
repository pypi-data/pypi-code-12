import struct
from threading import Lock

from pyrencode.settings import *


def encode_int(obj, data_list):
    if 0 <= obj < INT_POS_FIXED_COUNT:
        data_list.append(int2byte(INT_POS_FIXED_START + obj))
    elif -INT_NEG_FIXED_COUNT <= obj < 0:
        data_list.append(int2byte(INT_NEG_FIXED_START - 1 - obj))
    elif -INT1_SIZE <= obj < INT1_SIZE:
        data_list.extend((CHR_INT1, struct.pack('!b', obj)))
    elif -INT2_SIZE <= obj < INT2_SIZE:
        data_list.extend((CHR_INT2, struct.pack('!h', obj)))
    elif -INT4_SIZE <= obj < INT4_SIZE:
        data_list.extend((CHR_INT4, struct.pack('!l', obj)))
    elif -INT8_SIZE <= obj < INT8_SIZE:
        data_list.extend((CHR_INT8, struct.pack('!q', obj)))
    else:
        s = bytes(str(obj), 'ascii')
        if len(s) >= MAX_INT_LENGTH:
            raise OverflowError('Integer is too long to be rencoded.')

        data_list.extend((CHR_INT, s, CHR_TERM))


def encode_float32(obj, data_list):
    data_list.extend((CHR_FLOAT32, struct.pack('!f', obj)))


def encode_float64(obj, data_list):
    data_list.extend((CHR_FLOAT64, struct.pack('!d', obj)))


def encode_bool(obj, data_list):
    if obj:
        data_list.append(CHR_TRUE)
    else:
        data_list.append(CHR_FALSE)


def encode_none(_, data_list):
    data_list.append(CHR_NONE)


def encode_bytes(obj, data_list):
    if len(obj) < STR_FIXED_COUNT:
        data_list.extend((int2byte(STR_FIXED_START + len(obj)), obj))
    else:
        string = bytes(str(len(obj)), ASCII)
        data_list.extend((string, b':', obj))


def encode_string(obj, data_list):
    encode_bytes(obj.encode(UTF8), data_list)


def encode_list(obj, data_list):
    if len(obj) < LIST_FIXED_COUNT:
        data_list.append(int2byte(LIST_FIXED_START + len(obj)))
        for item in obj:
            encode_func[type(item)](item, data_list)
    else:
        data_list.append(CHR_LIST)
        for item in obj:
            encode_func[type(item)](item, data_list)
        data_list.append(CHR_TERM)


def encode_dict(obj, data_list):
    if len(obj) < DICT_FIXED_COUNT:
        data_list.append(int2byte(DICT_FIXED_START + len(obj)))
        for key, value in obj.items():
            encode_func[type(key)](key, data_list)
            encode_func[type(value)](value, data_list)
    else:
        data_list.append(CHR_DICT)
        for key, value in obj.items():
            encode_func[type(key)](key, data_list)
            encode_func[type(value)](value, data_list)
        data_list.append(CHR_TERM)


encode_func = {
    int: encode_int,
    bytes: encode_bytes,
    list: encode_list,
    tuple: encode_list,
    dict: encode_dict,
    type(None): encode_none,
    str: encode_string,
    bool: encode_bool,
}

lock = Lock()


def dumps(obj, float_bits=DEFAULT_FLOAT_BITS):
    data_list = None
    with lock:
        if float_bits == 32:
            encode_func[float] = encode_float32
        elif float_bits == 64:
            encode_func[float] = encode_float64
        else:
            raise ValueError(
                'Float bits {float_bits} is not 32 or 64'.format(
                    float_bits=float_bits
                )
            )
        data_list = []
        encode_func[type(obj)](obj, data_list)

    return b''.join(data_list)
