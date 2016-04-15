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

from threadloop import ThreadLoop

from yarpc.rpc import RPC as AsyncRPC
from yarpc.errors import YARPCError


class RPC(AsyncRPC):
    """YARPC from sync-python; can be used with outbounds only."""

    def __init__(self, service, outbounds=None, threadloop=None):
        super(RPC, self).__init__(
            service=service,
            inbounds=None,
            outbounds=outbounds,
        )
        self._threadloop = threadloop or ThreadLoop()

        # TODO switch to golang-style encoding clients
        self.call = _ThreadLoopCallable(self.call, self._threadloop)
        self.raw = _ThreadLoopCallable(self.raw, self._threadloop)
        self.json = _ThreadLoopCallable(self.json, self._threadloop)
        self.thrift = _ThreadLoopCallable(self.thrift, self._threadloop)

    def register(self, procedure, handler):
        raise SyncRegisterNotSupportedError(
            "Sync is client-only and does not support registration"
        )


class _ThreadLoopCallable(object):

    def __init__(self, fn, threadloop):
        self._fn = fn
        self._threadloop = threadloop

    def __call__(self, *args, **kwargs):
        if not self._threadloop.is_ready():
            self._threadloop.start()
        return self._threadloop.submit(self._fn, *args, **kwargs)


class SyncRegisterNotSupportedError(YARPCError):
    pass
