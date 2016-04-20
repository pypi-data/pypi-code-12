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
This module provides encoding and concurrency agnostic abstractions that
define how requests and responses can be encoded or decoded.

It defines an OutboundEncoder which can be used to encode outgoing requests
and decode their responses, and an InboundEncoder which can be used to decode
incoming requests and encode their responses.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)


# TODO: Define encode/decode exceptions. Encoders/decoders should raise only
# those exceptions and client implementations can handle them.

class OutboundEncoder(object):
    """Encodes outgoing requests and decodes their responses.

    .. code-block:: python

        request = encoder.encode_request(request)
        response = send(request)
        response = encoder.decode_response(response)

    Encoders are scoped to single requests and should not be re-used across
    multiple requests. The same encoder that was used to encode a request MUST
    be used to decode its response.
    """

    __slots__ = ()

    def encode_request(self, request):
        """Encodes the given request with this encoding.

        encode_request MUST be called before decode_response.

        This MAY mutate the underlying request or return a completely new
        request object. Callers should assume that they have lost ownership of
        the request object.

        :param yarpc.Request request:
            Request to encode
        :returns yarpc.Request:
            Encoded request
        """
        raise NotImplementedError

    def decode_response(self, response):
        """Decodes the given response with this encoding.

        encode_request MUST be called before decode_response.

        This MAY mutate the underlying response or return a completely new
        response object. Callers should assume that they have lost ownership
        of the response object.

        :param yarpc.Response response:
            Response to encode
        :returns yarpc.Response:
            Encoded response
        """
        raise NotImplementedError


class InboundEncoder(object):
    """Decodes incoming requests and encodes their responses or failures in
    handling the requests.

    .. code-block:: python

        try:
            request = encoder.decode_request(request)
            response = handle(request)
        except Exception:
            response = encoder.encode_exc_info(sys.exc_info())
        else:
            response = encoder.encode_response(response)

    Encoders are scoped to single requests and should not be re-used across
    multiple requests. The same encoder that was used to decode a request MUST
    be used to encode its response.
    """

    __slots__ = ()

    def decode_request(self, request):
        """Decodes the given request with this encoding.

        decode_request MUST be called before encode_response.

        This MAY mutate the underlying request or return a completely new
        request object. Callers should assume that they have lost ownership of
        the request object.

        :param yarpc.Request request:
            Request to encode
        :returns yarpc.Request:
            Encoded request
        """
        raise NotImplementedError

    def encode_response(self, response):
        """Encodes the given response with this encoding.

        decode_request MUST be called before encode_response. encode_response
        and encode_exc_info SHOULD return the same kind of object.

        This MAY mutate the underlying response or return a completely new
        response object. Callers should assume that they have lost ownership
        of the response object.

        :param yarpc.Response response:
            Response to encode
        :returns yarpc.Response:
            Encoded response
        """
        raise NotImplementedError

    def encode_exc_info(self, exc_info):
        """Encodes the given failure into a response.

        decode_request MUST be called before encode_exc_info. encode_response
        and encode_exc_info SHOULD return the same kind of object.

        This function MAY handle the exception and return a response. If it is
        unable to handle the exception, it MUST re-raise the exception.

        The default behavior is to re-raise the exception.

        :param tuple exc_info:
            Triple of ``(class, exception, traceback)`` representing the
            failure.
        :returns yarpc.Response:
            Encoded response
        """
        raise exc_info[0], exc_info[1], exc_info[2]


class SimpleEncoder(OutboundEncoder, InboundEncoder):
    """SimpleEncoder is an encoding for the simple case where request and
    response bodies are encoded in the same way and no local state is
    required.

    :param name:
        Name of the encoding.
    :param encode:
        A function that accepts the request/response body and returns bytes.
    :param decode:
        A function that accepts bytes and returns the request/response body.
    """

    __slots__ = ('name', 'encode', 'decode')

    def __init__(self, name, encode, decode):
        self.name = name
        self.encode = encode
        self.decode = decode

    def __str__(self):
        return 'SimpleEncoder(%s)' % self.name

    __repr__ = __str__

    def encode_request(self, request):
        request.encoding = self.name
        request.body = self.encode(request.body)
        return request

    def decode_request(self, request):
        request.body = self.decode(request.body)
        return request

    def encode_response(self, response):
        response.body = self.encode(response.body)
        return response

    def decode_response(self, response):
        response.body = self.decode(response.body)
        return response
