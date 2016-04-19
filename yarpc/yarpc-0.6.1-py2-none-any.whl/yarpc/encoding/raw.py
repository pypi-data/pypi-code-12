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

"""
This module provides the Raw encoding for YARPC.
"""

# TODO usage examples in docstring

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from ._encoding import SimpleEncoder
from ._async import AsyncClient, AsyncHandler


# TODO stuttering in naming.
# TODO limit the surface area of the exported API

def _identity(x):
    return x

#: RawEncoder provides the Raw encoding format.
RawEncoder = SimpleEncoder('raw', _identity, _identity)


class RawClient(object):
    """RawClient builds a client that sends raw requests via the given
    channel.

    .. code-block:: python

        client = RawClient(rpc.channel('myservice'))
        response = yield client.call(Request(
            procedure='hello',
            body='something',
        ))
    """

    __slots__ = ('_impl',)

    def __init__(self, channel):
        self._impl = AsyncClient(channel)

    @property
    def channel(self):
        return self._impl.channel

    def call(self, request):
        return self._impl.call(RawEncoder, request)


class RawHandler(object):
    """RawHandler wraps a raw procedure implementation into a transport
    level asynchronous Handler.
    """

    __slots__ = ('_impl',)

    def __init__(self, handler):
        self._impl = AsyncHandler(handler)

    @property
    def handler(self):
        return self._impl.handler

    def handle(self, request):
        return self._impl.handle(RawEncoder, request)


class RawProcedure(object):

    def __init__(self, name, handler):
        self.name = name

        # Handler is what the user gave us. We need to retain it so that they
        # can call it directly. transport_handler is what will get registered.
        self.handler = handler
        self.transport_handler = RawHandler(handler)

    @property
    def procedures(self):
        return {self.name: self.transport_handler}

    def __call__(self, *args, **kwargs):
        return self.handler(*args, **kwargs)


def procedure(name):
    """Builds a raw procedure. TODO explain.

    .. code-block:: python

        from yarpc.encoding import raw

        @raw.procedure('hello')
        def hello(request):
            return Response(body='foo')

        rpc.register(hello)

    Note that the decorated function can still be called directly with a raw
    request.

    .. code-block:: python

        hello(Request(body='foo'))
    """

    def decorator(f):
        return RawProcedure(name, f)

    return decorator
