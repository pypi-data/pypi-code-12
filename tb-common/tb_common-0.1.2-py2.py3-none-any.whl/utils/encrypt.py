import hashlib
from six import string_types

__author__ = 'hiepsimu'


def md5(text):
    try:
        if isinstance(text, string_types):
            text = text.decode('utf-8')
    except:
        pass

    return hashlib.md5(text.encode('utf-8')).hexdigest()
