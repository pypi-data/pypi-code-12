# coding: utf-8
"""
    pyextend.network.encoding
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    pyextend network encoding

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""

import base64


def b64decode_safe(s):
    s += (-len(s) % 4)*b'='
    return base64.b64decode(s)
