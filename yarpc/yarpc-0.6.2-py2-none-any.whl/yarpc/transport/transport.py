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
This module provides primitives for YARPC.

Types defined in this file MUST be agnostic of whether we're synchronous or
asynchornous.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)


class Request(object):

    def __init__(
        self,
        caller=None,
        service=None,
        encoding=None,
        ttl=None,
        procedure=None,
        headers=None,
        body=None,
    ):
        self.caller = caller
        self.service = service
        self.encoding = encoding
        self.ttl = ttl  # TODO what unit is this
        self.procedure = procedure
        self.headers = headers
        self.body = body

        # TODO maybe we want to create separate application-level Request
        # objects so that users don't accidentally set caller/service/encoding
        # since those are filled at a higher level


class Response(object):

    def __init__(self, headers=None, body=None):
        self.headers = headers
        self.body = body


class Outbound(object):

    __slots__ = ()

    def call(self, request):
        """Sends the given request over the wire and returns its response."""
        raise NotImplementedError


class Inbound(object):

    __slots__ = ()

    def start(self, handler):
        """Serves the given Handler over this Inbound.

        This MUST return immediately, although it SHOULD block until the
        Inbound is ready to accept requests.
        """
        raise NotImplementedError

    def stop(self):
        """Stops serving this Inbound.

        This MAY block while the server drains ongoing requests.
        """
        raise NotImplementedError


class Handler(object):

    __slots__ = ()

    def handle(self, request):
        """Handles the given request.

        Returns the Response for the given Request.
        """
        raise NotImplementedError


class Channel(object):
    """A Channel scopes an Outbound to a single caller-service pair.

    Channel-local settings take precedence over global RPC-level settings.
    """

    __slots__ = ('caller', 'service', 'outbound')

    def __init__(self, caller, service, outbound):
        self.caller = caller
        self.service = service
        self.outbound = outbound

        # TODO channel-local timeouts, etc.

    def call(self, request):
        # TODO do we always want to stomp the caller and service?
        request.caller = request.caller or self.caller
        request.service = request.service or self.service

        # TODO apply channel-local timeouts

        return self.outbound.call(request)


class Registrant(object):
    """Registrant provides zero or more procedures and their handlers."""

    __slots__ = ()

    @property
    def procedures(self):
        """Map from procedure name to Handler for that procedure."""
        raise NotImplementedError


class Procedure(Registrant, Handler):
    """Procedure is a Registrant that provides a single procedure and adapts a
    function which accepts a Request and returns a Response into a Handler.
    """

    __slots__ = ('name', 'handler')

    def __init__(self, name, handler):
        self.name = name
        self.handler = handler

    @property
    def procedures(self):
        return {self.name: self}

    def handle(self, request):
        return self.handler(request)

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, self.name)

    __repr__ = __str__
