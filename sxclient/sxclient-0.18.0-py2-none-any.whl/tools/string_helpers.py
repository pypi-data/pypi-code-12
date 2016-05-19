'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
__all__ = ['toutf8']


def toutf8(text):
    if isinstance(text, unicode):
        return text.encode('utf-8')
    elif isinstance(text, str):
        return text.decode('utf-8').encode('utf-8')
    else:
        raise TypeError(
            "Object is neither 'str' nor 'unicode': {}".format(repr(text))
        )
