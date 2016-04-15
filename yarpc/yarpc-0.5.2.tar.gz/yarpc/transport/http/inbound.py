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

from yarpc import Request
from yarpc._future import fail_to
from . import headers


class HTTPInbound(object):

    def __init__(self, port, reuse_port=False, handlers=None):
        self._port = port
        self._reuse_port = reuse_port
        self._handlers = handlers or []

    def start(self, dispatcher):
        self._handlers.append(
            ('.*$', _TornadoRequestHandler, dict(dispatcher=dispatcher)),
        )
        app = tornado.web.Application(
            handlers=self._handlers,
        )
        http_server = tornado.httpserver.HTTPServer(app)

        # the following does the same as http_server.listen(self._port),
        # except with fine grain control over the sockopts
        sockets = tornado.netutil.bind_sockets(
            port=self._port,
            reuse_port=self._reuse_port,
        )
        http_server.add_sockets(sockets)

    @property
    def hostport(self):
        # TODO get pub ip???
        return "localhost:%s" % self._port

    @property
    def port(self):
        return self._port


class _TornadoRequestHandler(tornado.web.RequestHandler):

    def initialize(self, dispatcher):
        self.dispatcher = dispatcher

    def post(self, path=None):

        # from request
        procedure = self.request.headers.get(headers.PROCEDURE)
        request = Request(
            caller=self.request.headers.get(headers.CALLER),
            service=self.request.headers.get(headers.SERVICE),
            encoding=self.request.headers.get(headers.ENCODING),
            procedure=procedure,
            body=self.request.body,
            hostport=self.request.headers.get(headers.HOSTPORT),
        )

        return_future = gen.Future()
        dispatch_future = gen.maybe_future(
            self.dispatcher.dispatch(request),
        )

        @fail_to(return_future)
        def dispatch_done(f):
            result = f.result()
            if result.body is not None:
                self.write(result.body)
            return_future.set_result(result)

        dispatch_future.add_done_callback(dispatch_done)

        return return_future
