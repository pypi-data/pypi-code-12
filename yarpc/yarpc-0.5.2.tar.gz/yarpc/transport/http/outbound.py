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

from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPRequest

from yarpc import Response
from yarpc._future import fail_to
from . import headers


class HTTPOutbound(object):

    def call(self, request):
        # this needs to be instantiated here to work with threadloop
        client = AsyncHTTPClient()
        http_request = HTTPRequest(
            url='http://%s/' % request.hostport,
            method='POST',
            headers={
                headers.CALLER: request.caller,
                headers.SERVICE: request.service,
                headers.ENCODING: request.encoding,
                headers.PROCEDURE: request.procedure,
                headers.HOSTPORT: request.hostport,
                headers.TTL: '10000',
            },
            body=request.body,
        )

        return_future = gen.Future()
        client_fetch_future = client.fetch(http_request)

        @fail_to(return_future)
        def client_fetch_done(f):
            result = f.result()
            response = Response(
                body=result.body,
            )
            return_future.set_result(response)

        client_fetch_future.add_done_callback(client_fetch_done)

        return return_future
