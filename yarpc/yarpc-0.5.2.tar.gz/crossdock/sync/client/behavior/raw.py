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

from crossdock import rand, transport
from yarpc import Request
from yarpc.sync import RPC


def raw(server, transport_name):
    rpc = RPC(
        service='client',
        outbounds={
            'yarpc-test': transport.factory(transport_name),
        },
    )

    expected = rand.string(7)

    request = Request(
        service='yarpc-test',
        procedure='echo/raw',
        body=expected,
        hostport="%s:%s" % (server, transport.port(transport_name)),
    )
    future = rpc.raw(request)
    response = future.result()

    if response.body != expected:
        raise Exception(
            "expected %s, got %s" % (expected, response.body)
        )

    return "Server said: %s" % response.body
