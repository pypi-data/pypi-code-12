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
import tornado.web
import tornado.httpserver
import tornado.netutil

from yarpc.transport import Inbound, Request
from yarpc._future import fail_to, maybe_async
from . import headers


class HTTPInbound(Inbound):

    def __init__(self, port, reuse_port=False, handlers=None):
        self.port = port
        self._reuse_port = reuse_port
        self._server = None
        self._handlers = handlers or []

    def start(self, handler):
        self._handlers.append(
            ('.*$', _TornadoRequestHandler, dict(handler=handler)),
        )
        app = tornado.web.Application(handlers=self._handlers)
        self._server = tornado.httpserver.HTTPServer(app)

        # the following does the same as http_server.listen(self.port),
        # except with fine grain control over the sockopts
        sockets = tornado.netutil.bind_sockets(
            port=self.port,
            reuse_port=self._reuse_port,
            # TODO update self.port (in case port was 0)
        )
        self._server.add_sockets(sockets)

    def stop(self):
        if self._server is not None:
            self._server.stop()
            self._server = None

    @property
    def hostport(self):
        # TODO get pub ip???
        return 'localhost:%s' % self.port


class _TornadoRequestHandler(tornado.web.RequestHandler):

    def initialize(self, handler):
        self.handler = handler

    def post(self):
        # TODO header validation
        http_headers = self.request.headers

        # required headers
        procedure = http_headers.pop(headers.PROCEDURE)
        caller = http_headers.pop(headers.CALLER)
        service = http_headers.pop(headers.SERVICE)

        # optional headers
        encoding = http_headers.pop(headers.ENCODING, None)

        request = Request(
            caller=caller,
            service=service,
            encoding=encoding,
            ttl=None,  # TODO
            procedure=procedure,
            headers=dict(http_headers),  # TODO
            body=self.request.body,
        )

        answer = gen.Future()

        @fail_to(answer)
        def on_dispatch(future):
            response = future.result()
            if response.body is not None:
                self.write(response.body)
            answer.set_result(None)

        maybe_async(
            self.handler.handle, request
        ).add_done_callback(on_dispatch)

        return answer
