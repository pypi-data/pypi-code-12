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
This module provides common, encoding-agnostic functionality for Tornado. It
should not be used outside the encoding package.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from tornado import gen

from yarpc._future import transform, fail_to, maybe_async
from yarpc import transport


class AsyncClient(object):
    """Encoding agnostic asynchronous client.

    :param channel:
        Channel through which requests will be sent.
    """

    def __init__(self, channel):
        self.channel = channel

    def call(self, encoder, request):
        request = encoder.encode_request(request)
        future = self.channel.call(request)
        return transform(future, encoder.decode_response)


class AsyncHandler(transport.Handler):
    """Encoding agnsotic asynchronous handler.

    Wraps a handler of the given encoding type to speak raw bytes and act as a
    transport-level handler.

    :param handler:
        A function that accepts a request and returns its response or a future
        that resolves to the response.
    """

    def __init__(self, handler):
        self.handler = handler
        # NOTE: Transport-level Handlers have a handle() method but
        # encoding-level handlers are just functions that accept a Request and
        # return a Future<Response>.

    def handle(self, encoder, request):
        request = encoder.decode_request(request)
        answer = gen.Future()

        @fail_to(answer)
        def on_done(future):
            if future.exception():
                response = encoder.encode_exc_info(future.exc_info())
            else:
                response = encoder.encode_response(future.result())
            answer.set_result(response)

        maybe_async(self.handler, request).add_done_callback(on_done)
        return answer
