# Copyright (c) 2016 Uber Technologies, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import json
import struct
from io import BytesIO

from tchannel.schemes import JSON


def encode(scheme, headers):
    headers = headers or {}
    if scheme == JSON:
        return json.dumps(headers)
    return _encode(headers)


def decode(scheme, src):
    if not src:
        return {}
    if scheme == JSON:
        return json.loads(src)
    return _decode(BytesIO(src))


def _encode(headers):
    """Writes headers in the format ``nh:2 (k~2 v~2){nh}``."""

    out = BytesIO()
    _put_i16(out, len(headers))  # nh:2

    for k, v in headers.items():
        _put_str16(out, k)  # k~2
        _put_str16(out, v)  # v~2

    return out.getvalue()


def _decode(src):
    """Readers headers in the format ``nh:2 (k~2 v~2){nh}``."""

    num = _get_i16(src)
    headers = {}

    for i in xrange(num):
        k = _get_str16(src)
        v = _get_str16(src)
        headers[k] = v

    return headers


def _put_str16(out, s):
    """Writes a string in the format ``len(s):2 s:*``"""
    _put_i16(out, len(s))  # len(s):2
    out.write(s)


def _get_str16(src):
    """Reads a string in the format ``len(s):2 s:*``"""
    length = _get_i16(src)
    s = src.read(length)
    assert len(s) == length, (
        'expected %d bytes, got %d' % (length, len(s))
    )  # TODO explicit decode exception
    return s


def _put_i16(out, i):
    """Writes a 16-bit integer in big-endian byte-order."""
    out.write(struct.pack('>H', i))


def _get_i16(src):
    """Reades a 16-bit integer in big-endian byte-order."""
    s = src.read(2)
    assert len(s) == 2, 'ran out of input'  # TODO explicit decode exception
    return struct.unpack('>H', s)[0]
