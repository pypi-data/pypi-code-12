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

from .dispatcher import Dispatcher
from .encoding import RawEncoding, JsonEncoding, ThriftEncoding


class RPC(object):

    def __init__(self, service, inbounds=None, outbounds=None):
        self._service = service
        self._inbounds = inbounds

        if outbounds is None:
            self._outbounds = {}
        else:
            self._outbounds = outbounds

        self._dispatcher = Dispatcher()

        # TODO encodings should be injectable
        self.raw = RawEncoding(self)
        self.json = JsonEncoding(self)
        self.thrift = ThriftEncoding(self)

    def register(self, procedure, handler):
        self._dispatcher.register(procedure, handler)

    def start(self):
        return [
            gen.maybe_future(inbound.start(self._dispatcher))
            for inbound in self._inbounds
        ]

    def call(self, request):
        assert request.service, "service is required"
        assert request.encoding, "encoding is required"
        assert request.procedure, "procedure is required"

        request.caller = self._service

        outbound = self._outbounds.get(request.service)
        return_future = outbound.call(request)

        return return_future
