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

"""
This module provides the Thrift encoding for YARPC.
"""

# TODO usage examples in docstring

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from types import ModuleType

import thriftrw

from yarpc.errors import ValueExpectedError, OneWayNotSupportedError
from yarpc.transport import Response
from ._encoding import OutboundEncoder, InboundEncoder
from ._async import AsyncClient, AsyncHandler


NAME = 'thrift'

# TODO stuttering? do we really want everything to have Thrift in front of its
# name even though we have namespaces?

# TODO perhaps we should introduce a Thrift-only Request type which makes it
# impossible to set the procedure.

# TODO Move the load(...) logic and types into a non-public submodule of this
# package.


def load(path):
    """Loads the Thrift file at the given path."""
    return _wrap(thriftrw.load(path))


def _wrap(thriftrw_module):
    """Wraps a thriftrw module to generate requests for YARPC."""

    module = ModuleType(thriftrw_module.__name__)

    # Attach services
    for s in thriftrw_module.__services__:
        setattr(module, s.service_spec.name, Service(module, s))

    # Attach types
    for t in thriftrw_module.__types__:
        # Workaround for thriftrw/thriftrw-python#124
        if hasattr(t, '__name__'):
            setattr(module, t.__name__, t)

    # Attach constants
    for n, c in thriftrw_module.__constants__.items():
        setattr(module, n, c)

    # Attach includes
    for m in thriftrw_module.__includes__:
        setattr(module, m.__name__, m)

    return module


class Service(object):

    def __init__(self, module, service_cls):
        self.service_cls = service_cls
        self.service_spec = service_cls.service_spec

        for func_spec in self.service_spec.functions:
            setattr(self, func_spec.name, Function(module, self, func_spec))

    @property
    def name(self):
        return self.service_spec.name

    def __str__(self):
        return 'Service(%s)' % self.name

    __repr__ = __str__


class Function(object):

    def __init__(self, module, service, func_spec):
        self.spec = func_spec
        self.service = service

        function = func_spec.surface
        self._request_cls = function.request
        self._response_cls = function.response

    @property
    def name(self):
        return '%s::%s' % (self.service.name, self.spec.name)

    def __str__(self):
        return 'Function(%s)' % self.name

    __repr__ = __str__

    def __call__(self, *args, **kwargs):
        if self.spec.oneway:
            raise OneWayNotSupportedError(
                'YARPC does not currently support oneway procedures.'
            )
        return self._request_cls(*args, **kwargs)


class ThriftClient(object):
    """ThriftClient builds a client that sends Thrift requests via the given
    channel.

    .. code-block:: python

        foo = thrift.load('foo.thrift')
        client = thrift.ThriftClient(rpc.channel('foo'))

        response = yield client.call(Request(
            headers={'foo': 'bar'},
            body=foo.MyService.someMethod(arg1, arg2),
        ))
    """

    __slots__ = ('_impl',)

    def __init__(self, channel):
        self._impl = AsyncClient(channel)

    @property
    def channel(self):
        return self._impl.channel

    def call(self, request):
        encoder = _OutboundEncoder()
        return self._impl.call(encoder, request)


class _OutboundEncoder(OutboundEncoder):

    def __init__(self):
        self.module = None
        self.result_spec = None

    def encode_request(self, request):
        thrift_request = request.body
        request_cls = thrift_request.__class__
        function_spec = request_cls.type_spec.function
        service_spec = function_spec.service

        self.module = thrift_request.__thrift_module__
        self.result_spec = request_cls.result_type.type_spec

        request.encoding = NAME
        request.procedure = _get_procedure_name(
            service=service_spec.name,
            function=function_spec.name,
        )

        request.body = self.module.dumps(request.body)
        return request

    def decode_response(self, response):
        thrift_response = self.module.loads(
            self.result_spec.surface,
            response.body,
        )
        response.body = _unwrap_body(
            response_spec=self.result_spec,
            body=thrift_response,
        )
        return response


class _InboundEncoder(InboundEncoder):

    def __init__(self, function_spec):
        self.function_spec = function_spec
        self.args_spec = function_spec.args_spec
        self.result_spec = function_spec.result_spec
        self.module = self.args_spec.surface.__thrift_module__

    def decode_request(self, request):
        request.body = self.module.loads(self.args_spec.surface, request.body)
        return request

    def encode_response(self, response):
        if response.body is None:
            # TODO separate exception
            assert self.result_spec.return_spec is None, (
                'Expected a value to be returned for %s, '
                'but recieved None - only void procedures can '
                'return None.' % self.function_spec.name
            )
            response.body = self.result_spec.surface()
        else:
            response.body = self.result_spec.surface(success=response.body)
        response.body = self.module.dumps(response.body)
        return response

    def encode_exc_info(self, exc_info):
        response_body = None

        e = exc_info[1]
        for exc_spec in self.result_spec.exception_specs:
            if isinstance(e, exc_spec.spec.surface):
                response_body = self.result_spec.surface(**{exc_spec.name: e})
                break

        if response_body is not None:
            response_body = self.module.dumps(response_body)
            return Response(body=response_body)

        # No match. Re-raise.
        raise exc_info[0], exc_info[1], exc_info[2]


class ThriftHandler(object):

    __slots__ = ('_impl', 'function_spec')

    def __init__(self, function_spec, handler):
        self.function_spec = function_spec
        self._impl = AsyncHandler(handler)

    @property
    def handler(self):
        return self._impl.handler

    def handle(self, request):
        encoder = _InboundEncoder(self.function_spec)
        return self._impl.handle(encoder, request)


class ThriftProcedure(object):

    def __init__(self, service_spec, function_spec, handler):
        self.name = _get_procedure_name(
            service=service_spec.name,
            function=function_spec.name,
        )
        self.handler = handler

        self.transport_handler = ThriftHandler(function_spec, handler)

    @property
    def procedures(self):
        return {self.name: self.transport_handler}

    def __call__(self, *args, **kwargs):
        return self.handler(*args, **kwargs)


def procedure(service, method=None):
    """Builds a Thrift procedure.

    .. code-block:: python

        from yarpc.encoding import thrift

        foo = thrift.load('foo.thrift')

        @thrift.procedure(foo.MyService)
        def someMethod(request):
            # ...
    """

    def decorator(f):
        function = method
        if function is None:
            function = f.__name__
        function = getattr(service, function)
        # TODO raise more user friendly exception on AttributeError.
        return ThriftProcedure(service.service_spec, function.spec, f)

    return decorator


def _get_procedure_name(service, function):
    return '%s::%s' % (service, function)


def _unwrap_body(response_spec, body):

    # exception - reraise
    for exc_spec in response_spec.exception_specs:
        exc = getattr(body, exc_spec.name)
        if exc is not None:
            raise exc

    # success - non-void
    if response_spec.return_spec is not None:
        if body.success is None:
            raise ValueExpectedError(
                'Expected a value to be returned in %s, but received '
                'None. Only void procedures can return None.'
                % str(response_spec.surface)
            )

        return body.success

    # success - void
    else:
        return None
