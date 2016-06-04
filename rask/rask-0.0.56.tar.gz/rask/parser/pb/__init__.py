from base64 import b64decode,b64encode

__all__ = [
    'decode',
    'encode'
]

def decode(msg,proto):
    proto.ParseFromString(b64decode(msg))
    return proto

def encode(proto):
    return b64encode(proto.SerializeToString())
