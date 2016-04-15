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
from tchannel import TChannel, Response
from tchannel.serializer import json, thrift
from tchannel.sync import TChannel as TChannelSync

from yarpc import Request, encoding
from yarpc._future import fail_to


class TChannelInbound(object):

    def __init__(self, tchannel):
        if isinstance(tchannel, TChannelSync):
            raise ValueError(
                "TChannelInbound must use a regular TChannel,"
                "do not use a TChannelSync"
            )
        self._tchannel = tchannel

    def start(self, dispatcher):
        @self._tchannel.register(TChannel.FALLBACK)
        def handler(request):
            procedure = request.endpoint

            yarpc_req = Request(
                caller=request.transport.caller_name,
                service=request.service,
                encoding=request.transport.scheme,
                procedure=procedure,
                body=request.body,
                hostport=self._tchannel.hostport,
            )

            return_future = gen.Future()
            dispatch_future = gen.maybe_future(
                dispatcher.dispatch(yarpc_req),
            )

            # TODO handle headers
            if yarpc_req.encoding == encoding.JSON:
                serializer = json.JsonSerializer()
            else:
                serializer = thrift.ThriftSerializer(None)
            headers = serializer.serialize_header(None)

            @fail_to(return_future)
            def dispatch_done(f):
                result = f.result()
                response = Response(
                    body=result.body,
                    headers=headers,
                    transport=None,  # TODO transport?
                )
                return_future.set_result(response)

            dispatch_future.add_done_callback(dispatch_done)

            return return_future

        if not self._tchannel.is_listening():
            self._tchannel.listen()

    @property
    def hostport(self):
        return self._tchannel.hostport

    @property
    def port(self):
        return int(self.hostport.rsplit(':', 1)[1])
