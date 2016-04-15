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

from tornado import gen

from . import THRIFT
from yarpc.request import Request
from yarpc.errors import ValueExpectedError
from yarpc._future import fail_to


class ThriftEncoding(object):

    # TODO based on transport properties, do the following:
    # some outbounds, like tchannel, expect no enveloping on thrift payload
    # outbound = self._rpc.get_outbound(request.service)
    # envelope = getattr(outbound, 'ENVELOPE_THRIFT', True)
    _envelope = False

    NAME = THRIFT

    def __init__(self, rpc):
        self._rpc = rpc

    def __call__(self, request=None, **kwargs):
        if request is None:
            request = Request(**kwargs)

        request.encoding = self.NAME

        thrift_request = request.body
        thrift_module = thrift_request.__thrift_module__
        function_spec = thrift_request.type_spec.function
        service_spec = function_spec.service

        # get service from thrift.load, if not provided
        if request.service is None:
            request.service = thrift_request.__class__.service_name

        request.procedure = _get_procedure_name(
            service=service_spec.name,
            function=function_spec.name,
        )

        # serialize body based on envelope bool
        if self._envelope is True:
            request.body = thrift_module.dumps.message(request.body)
        else:
            request.body = thrift_module.dumps(request.body)

        return_future = gen.Future()
        rpc_call_future = self._rpc.call(request)

        @fail_to(return_future)
        def rpc_call_done(f):
            result = f.result()
            if self._envelope is True:
                thrift_response = thrift_module.loads.message(
                    service_spec.surface,
                    result.body,
                ).body
            else:
                thrift_response = thrift_module.loads(
                    thrift_request.result_type,
                    result.body,
                )
            result.body = _unwrap_body(
                response_spec=thrift_request.result_type.type_spec,
                body=thrift_response,
                procedure=request.procedure
            )
            return_future.set_result(result)

        rpc_call_future.add_done_callback(rpc_call_done)

        return return_future

    def register(self, thrift_service, handler):
        # TODO enable calling with decorator

        procedure = _get_procedure_name(
            service=thrift_service.name,
            function=handler.__name__,
        )
        function = getattr(thrift_service, handler.__name__)

        thrift_request_cls = function.request
        thrift_module = thrift_request_cls.__thrift_module__

        @wraps(handler)
        def wrapped(request):

            # deserialize
            if self._envelope is True:
                request.body = thrift_module.loads.message(
                    thrift_service,
                    request.body,
                ).body
            else:
                request.body = thrift_module.loads(
                    thrift_request_cls,
                    request.body,
                )

            # execute procedure
            response_future = gen.maybe_future(handler(request))

            def on_got_response(f):
                # TODO: f.exception()
                response = f.result()
                # serialize
                response.body = function.response_cls(success=response.body)
                if self._envelope is True:
                    response.body = thrift_module.dumps.message(response.body)
                else:
                    response.body = thrift_module.dumps(response.body)

            response_future.add_done_callback(on_got_response)

            return response_future

        self._rpc.register(procedure, wrapped)


def _get_procedure_name(service, function):
    return '%s::%s' % (service, function)


def _unwrap_body(response_spec, body, procedure):

    # exception - reraise
    for exc_spec in response_spec.exception_specs:
        exc = getattr(body, exc_spec.name)
        if exc is not None:
            raise exc

    # success - non-void
    if response_spec.return_spec is not None:
        if body.success is None:
            raise ValueExpectedError(
                'Expected a value to be returned for %s, '
                'but recieved None - only void procedures can '
                'return None.' % procedure
            )

        return body.success

    # success - void
    else:
        return None
