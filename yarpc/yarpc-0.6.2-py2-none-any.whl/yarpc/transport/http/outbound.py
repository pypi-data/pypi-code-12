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

from yarpc.transport import Outbound, Response
from yarpc._future import fail_to
from . import headers


class HTTPOutbound(Outbound):
    """

    :param str url:
        URL to which HTTP requests will be sent.
    :param AsyncHTTPClient client:
        HTTP client used to make requests. A default client will be
        constructed if omitted.
    """

    def __init__(self, url, client=None):
        self.url = url

        # We don't build the default client here because if we're using
        # threadloop, we want the IOLoop of the threadloop to be used by the
        # AsyncHTTPClient but it resolves the IOLoop at instantiation.
        self.client = client

    def call(self, request):
        if self.client is None:
            self.client = AsyncHTTPClient()

        http_headers = dict(request.headers or {})
        http_headers.update({
            headers.CALLER: request.caller,
            headers.SERVICE: request.service,
            headers.ENCODING: request.encoding,
            headers.TTL: '10000',  # TODO
            headers.PROCEDURE: request.procedure,
        })

        http_request = HTTPRequest(
            url=self.url,
            method='POST',
            headers=http_headers,
            body=request.body,
            # request_timeout=None,  TODO
        )

        answer = gen.Future()

        @fail_to(answer)
        def on_fetch(f):
            result = f.result()

            response = Response(
                headers=None,  # TODO
                body=result.body,
            )
            answer.set_result(response)

        self.client.fetch(http_request).add_done_callback(on_fetch)
        return answer
