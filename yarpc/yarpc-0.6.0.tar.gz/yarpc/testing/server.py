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

from threading import Thread

import tornado.ioloop


class ThreadedServer(object):
    """Start a YARPC server in a background thread."""

    def __init__(self, rpc):
        self._thread = None
        self._ready = False
        self._rpc = rpc

    def start(self):
        assert self._thread is None, 'thread already started'
        self._thread = Thread(target=self._init)
        self._thread.start()
        while not self._ready:
            pass

        # TODO don't use spinlock

    def stop(self):
        self.io_loop.stop()
        self._rpc.stop()
        self._thread.join()

    def _init(self):
        self.io_loop = tornado.ioloop.IOLoop()
        self.io_loop.make_current()

        self._rpc.start()

        def callback():
            self._ready = True

        self.io_loop.add_callback(callback)
        self.io_loop.start()
