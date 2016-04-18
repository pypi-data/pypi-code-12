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
from tchannel.sync import TChannel as TChannelSync

from yarpc.transport import Inbound, Request
from yarpc._future import fail_to, maybe_async
from . import headers


class TChannelInbound(Inbound):

    def __init__(self, tchannel):
        if isinstance(tchannel, TChannelSync):
            raise ValueError(
                "TChannelInbound must use a regular TChannel,"
                "do not use a TChannelSync"
            )
        self._tchannel = tchannel

    def start(self, handler):
        self._tchannel.register(TChannel.FALLBACK)(_TChanHandler(handler))
        if not self._tchannel.is_listening():
            self._tchannel.listen()

    def stop(self):
        # https://github.com/uber/tchannel-python/issues/407
        self._tchannel._dep_tchannel.close()  # :(

    @property
    def hostport(self):
        return self._tchannel.hostport

    @property
    def port(self):
        return int(self.hostport.rsplit(':', 1)[1])


class _TChanHandler(object):

    def __init__(self, handler):
        self.handler = handler

    def __call__(self, tchan_request):
        scheme = tchan_request.transport.scheme
        request = Request(
            caller=tchan_request.transport.caller_name,
            service=tchan_request.service,
            encoding=scheme,
            # ttl=None
            procedure=tchan_request.endpoint,
            headers=headers.decode(scheme, tchan_request.headers),
            body=tchan_request.body,
        )

        answer = gen.Future()

        @fail_to(answer)
        def on_dispatch(future):
            response = future.result()
            tchan_response = Response(
                body=response.body,
                headers=headers.encode(scheme, response.headers),
                transport=None,  # TODO transport?
            )
            answer.set_result(tchan_response)

        maybe_async(
            self.handler.handle, request
        ).add_done_callback(on_dispatch)

        return answer
