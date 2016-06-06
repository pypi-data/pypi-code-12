# -*- coding: utf-8 -*-

"""
requestests.api
~~~~~~~~~~~~

This module extends the Requests API for testing purposes.

:copyright: (c) 2016 by Peter Salas.
:license: Apache2, see LICENSE for more details.

"""

import jsonstruct
import re
import requests
from requests.models import Response


def json_decode(self, serializable_class):
    """Provides a convenience method to Response to deserialize directly into a specific Object type of choice.
    Behind the scenes, this is using jsonstruct for decoding.

    :param serializable_class
    :return instance of serializable_class
    """

    return jsonstruct.decode(self.text, serializable_class)


def validate_code(self, code):
    """Validates response code

    :param code: The expected response code
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    :raises: AssertionError, if the response.code != code
    """

    assert self.status_code == code
    return self


def validate_not_code(self, code):
    """Validates response code

    :param code: The not expected response code
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    :raises: AssertionError, if the response.code == code
    """

    assert self.status_code != code
    return self


def validate_codes(self, codes=[]):
    """Validates response codes

    :param codes: A list of expected response codes
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    :raises: AssertionError, if none of the response.code were returned. At least 1 must match
    """

    result = False
    for code in codes:
        result = (result or self.status_code == code)
    assert result
    return self


def validate_not_codes(self, codes=[]):
    """Validates response codes not returned

    :param codes: A list of unexpected response codes
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    :raises: AssertionError, if one of the response.code were returned.
    """

    result = False
    for code in codes:
        result = (result or self.status_code == code)
    assert not result, "Expected response should not to contain these codes: {}".format(', '.join(map(str, codes)))
    return self


def validate_header_eq(self, header, value):
    """Validates header equals

    :param header: The header to check
    :param value: The value that you expect the header to be
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    :raises: AssertionError, if header does not match
    """

    assert self.headers[header] == value
    return self


def validate_header_like(self, header, value):
    """Validates header using regular expression

    :param header: The header to check
    :param value: The value that you expect the header to be
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    :raises: AssertionError, if header does not match
    """

    assert re.search(value, self.headers[header])
    return self


def validate_content(self, value):
    """Validates content body using regular expression

    :param value: The value that you expect the body to be/have
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    :raises: AssertionError, if body does not match
    """

    assert re.search(value, self.text)
    return self


def validate_entity_eq(self, value):
    """Validates content body

    :param value: The value that you expect the body to be. This should be an instance of a deserializable entity
                    (a.k.a. representational entity)
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    :raises: AssertionError, if objects do not match
    """

    entity = self.json_decode(value.__class__)
    assert entity == value, "{} == {}".format(str(entity), str(value))
    return self


# Code to extend the existing requests.Response object
Response.json_decode = json_decode
Response.validate_code = validate_code
Response.validate_not_code = validate_not_code
Response.validate_codes = validate_codes
Response.validate_not_codes = validate_not_codes
Response.validate_header_eq = validate_header_eq
Response.validate_header_like = validate_header_like
Response.validate_content = validate_content
Response.validate_entity_eq = validate_entity_eq


def get(url, params=None, **kwargs):
    """Sends a GET request.

    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.get(url, params=params, **kwargs)


def options(url, **kwargs):
    """Sends a OPTIONS request.

    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.options(url, **kwargs)


def head(url, **kwargs):
    """Sends a HEAD request.

    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.head(url, **kwargs)


def post(url, data=None, json=None, **kwargs):
    """Sends a POST request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.post(url, data=data, json=json, **kwargs)


def put(url, data=None, **kwargs):
    """Sends a PUT request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.put(url, data=data, **kwargs)


def patch(url, data=None, **kwargs):
    """Sends a PATCH request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.patch(url, data=data, **kwargs)


def delete(url, **kwargs):
    """Sends a DELETE request.

    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.delete(url, **kwargs)
