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
This module provides the JSON encoding for YARPC.
"""

# TODO usage examples in docstring

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import json

from ._encoding import SimpleEncoder
from ._async import AsyncClient, AsyncHandler


# TODO stuttering? do we really want everything to have JSON in front of its
# name even though we have namespaces?
# TODO limit the surface area of the exported API


#: JSONEncoder uses JSON to encode/decode request bodies.
JSONEncoder = SimpleEncoder('json', json.dumps, json.loads)


class JSONClient(object):
    """JSONClient builds a JSON client that sends requests via the given
    channel.

    .. code-block:: python

        client = JSONClient(rpc.channel('myservice'))
        response = yield client.call(Request(
            procedure='hello',
            headers={'token': 'foo'},
            body={'name': 'somecaller'},
        ))
    """

    __slots__ = ('_impl',)

    def __init__(self, channel):
        self._impl = AsyncClient(channel)

    @property
    def channel(self):
        return self._impl.channel

    def call(self, request):
        return self._impl.call(JSONEncoder, request)


class JSONHandler(object):
    """JSONHandler wraps a JSON procedure implementation into a transport
    level asynchronous Handler.
    """

    __slots__ = ('_impl',)

    def __init__(self, handler):
        self._impl = AsyncHandler(handler)

    @property
    def handler(self):
        return self._impl.handler

    def handle(self, request):
        return self._impl.handle(JSONEncoder, request)


class JSONProcedure(object):

    def __init__(self, name, handler):
        self.name = name

        # Handler is what the user gave us. We need to retain it so that they
        # can call it directly. transport_handler is what will get registered.
        self.handler = handler
        self.transport_handler = JSONHandler(handler)

    @property
    def procedures(self):
        return {self.name: self.transport_handler}

    def __call__(self, *args, **kwargs):
        return self.handler(*args, **kwargs)


def procedure(name):
    """Builds a JSON procedure. TODO explain.

    .. code-block:: python

        from yarpc.encoding import json

        @json.procedure('hello')
        def hello(request):
            print(request.headers)
            return Response(body={
                'success': 'hello, %s' % request.body['name']
            })

        rpc.register(hello)

    Note that the decorated function can still be called directly with a JSON
    request.

    .. code-block:: python

        hello(Request(body={'foo': 'bar'}))
    """

    def decorator(f):
        return JSONProcedure(name, f)

    return decorator
