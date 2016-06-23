from base64 import b64decode,b64encode

__all__ = [
    'decode',
    'encode'
]

def decode(msg,proto):
    try:
        proto.ParseFromString(b64decode(msg))
    except TypeError:
        return False
    except:
        raise
    return proto

def encode(proto):
    return b64encode(proto.SerializeToString())
