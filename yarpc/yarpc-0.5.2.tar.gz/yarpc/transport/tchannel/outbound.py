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

from tchannel.serializer import json, thrift
from tornado import gen

from yarpc import Response, encoding
from yarpc._future import fail_to


class TChannelOutbound(object):

    def __init__(self, tchannel):
        self._tchannel = tchannel

    def call(self, request):

        # TODO handle headers
        if request.encoding == encoding.JSON:
            serializer = json.JsonSerializer()
        else:
            serializer = thrift.ThriftSerializer(None)
        headers = serializer.serialize_header(None)

        # TODO use tchannel.request once mash lands
        call_args = {
            'scheme': request.encoding,
            'service': request.service,
            'arg1': request.procedure,
            'arg2': headers,
            'arg3': request.body,
            'timeout': None,  # TODO timeout
            'retry_on': None,  # TODO retry_on
            'routing_delegate': None,
            'hostport': request.hostport,
            'shard_key': None,
            'trace': None,  # TODO trace
        }

        return_future = gen.Future()
        tchannel_call_future = self._tchannel.call(**call_args)

        @fail_to(return_future)
        def tchannel_call_done(f):
            result = f.result()
            response = Response(
                body=result.body,
            )
            return_future.set_result(response)

        tchannel_call_future.add_done_callback(tchannel_call_done)

        return return_future
