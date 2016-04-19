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


class _ThreadLoopCallable(object):

    def __init__(self, fn, threadloop):
        self._fn = fn
        self._threadloop = threadloop

    def __call__(self, *args, **kwargs):
        if not self._threadloop.is_ready():
            self._threadloop.start()
        return self._threadloop.submit(self._fn, *args, **kwargs)


class _ThreadLoopDelegate(object):

    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        func = getattr(instance._delegate, self.name)
        return _ThreadLoopCallable(func, instance._threadloop)


class RPC(object):
    """YARPC from sync-python; can be used with outbounds only."""

    __slots__ = ('_rpc', '_threadloop')

    def __init__(self, service, outbounds=None, threadloop=None):
        self._rpc = AsyncRPC(
            service=service,
            inbounds=None,
            outbounds=outbounds,
        )
        self._threadloop = threadloop or ThreadLoop()

    @property
    def service(self):
        return self._rpc.service

    def channel(self, *args, **kwargs):
        channel = self._rpc.channel(*args, **kwargs)
        return Channel(channel, self._threadloop)

    def register(self, *args, **kwargs):
        raise SyncRegisterNotSupportedError(
            "Sync is client-only and does not support registration"
        )


class Channel(object):

    def __init__(self, channel, threadloop):
        self._delegate = channel
        self._threadloop = threadloop

    def __getattr__(self, attr):
        return getattr(self._delegate, attr)

    def __setattr__(self, name, value):
        if name in ('_delegate', '_threadloop'):
            self.__dict__[name] = value
        else:
            setattr(self._delegate, name, value)

    call = _ThreadLoopDelegate('call')


class SyncRegisterNotSupportedError(YARPCError):
    pass
