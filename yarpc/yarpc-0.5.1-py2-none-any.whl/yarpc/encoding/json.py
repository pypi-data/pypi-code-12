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

from functools import wraps
import json

from tornado import gen

from . import JSON
from yarpc.request import Request
from yarpc._future import fail_to


class JsonEncoding(object):
    # TODO: This object model still feels too complicated. I just want to
    # define a serialize/deserialize method, and the handler I register applies
    # that encoding....

    NAME = JSON

    def __init__(self, rpc):
        self._rpc = rpc

    def __call__(self, request=None, **kwargs):
        if request is None:
            request = Request(**kwargs)

        # serialize
        request.encoding = self.NAME
        request.body = json.dumps(request.body)

        return_future = gen.Future()
        rpc_call_future = self._rpc.call(request)

        @fail_to(return_future)
        def rpc_call_done(f):
            result = f.result()
            result.body = json.loads(result.body)
            return_future.set_result(result)

        rpc_call_future.add_done_callback(rpc_call_done)

        return return_future

    def register(self, procedure, handler):
        @wraps(handler)
        def wrapped(request):

            # deserialize
            request.body = json.loads(request.body)

            return_future = gen.Future()
            handler_future = gen.maybe_future(handler(request))

            @fail_to(return_future)
            def handler_done(f):
                result = f.result()
                result.body = json.dumps(result.body)
                return_future.set_result(result)

            handler_future.add_done_callback(handler_done)

            return return_future

        self._rpc.register(procedure, wrapped)
