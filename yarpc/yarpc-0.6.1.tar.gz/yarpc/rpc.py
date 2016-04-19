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


from yarpc.transport import Channel


class RPC(object):

    def __init__(self, service, inbounds=None, outbounds=None):
        self.service = service
        self._inbounds = inbounds
        self._outbounds = outbounds or {}
        self._dispatcher = _Dispatcher()

    def register(self, registrant):
        # TODO decorator and register(procedure, handler) versions.
        self._dispatcher.register(registrant)

    def start(self):
        for inbound in self._inbounds:
            inbound.start(self)

    def stop(self):
        for inbound in self._inbounds:
            inbound.stop()

    def handle(self, request):
        return self._dispatcher.handle(request)

    def channel(self, service):
        assert service, "service is required"
        outbound = self._outbounds[service]
        # TODO unknown service error
        return Channel(
            caller=self.service,
            service=service,
            outbound=outbound,
        )


class _Dispatcher(object):
    """A Handler which allows registering multiple procedures."""

    def __init__(self):
        self._procedures = {}

    def register(self, registrant):
        for procedure, handler in registrant.procedures.items():
            self._procedures[procedure] = handler

    def handle(self, request):
        procedure = self._procedures.get(request.procedure)

        assert procedure, ("unknown procedure %s" % procedure)
        # TODO unknown endpoint error

        # TODO enable returning just body, instead of request
        response = procedure.handle(request)
        return response
