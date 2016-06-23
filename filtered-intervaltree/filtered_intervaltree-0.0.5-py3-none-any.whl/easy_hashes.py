import struct
import hashlib
from typing import Callable, List
import mmh3


def hash_to_64(value: str, count:int=1) -> List[int]:
    """
    gets a list of numbers between 0 and 63 for use in a filter vector
    :param value: string to be hashed
    :param count: must be less than 6
    :return:
    """
    digest = mmh3.hash_bytes(value)
    results = []
    for i in range(0, count):
        bytes = digest[i * 2:i * 2 + 2]
        value = struct.unpack("h", bytes)
        results.append(value[0] % 64)
    return results


def hashalg_to_64(value: str, func: Callable[[bytes], hashlib._hashlib.HASH]=hashlib.sha256, count=1):
    t_value = value.encode('utf8')
    digest = func(t_value).digest()

    results = []
    for i in range(0, count):
        bytes = digest[i*2:i*2+2]
        value = struct.unpack("h", bytes)
        results.append(value[0] % 64)
    return results
