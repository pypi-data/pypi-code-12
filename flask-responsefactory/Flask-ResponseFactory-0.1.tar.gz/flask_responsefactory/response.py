"""Module contains Response class. The Response class follows the factory
pattern for producing Flask's Response object with applicable HTTP status codes.
"""


import json

from flask import Response as FlaskResponse


class Response(object):
    """Factory class producing Flask Response objects with applicable HTTP
    status codes"""

    status_code = 200

    @classmethod
    def status(cls, status_code):
        """Set status_code class variable"""
        cls.status_code = status_code

        return cls

    @classmethod
    def build(cls, rv=None):
        """Return Flask Response object"""
        response = FlaskResponse(rv)
        response.status_code = cls.status_code

        return response

    @classmethod
    def json(cls, payload):
        """Return Flask Response object with serialized JSON payload"""
        response = FlaskResponse(json.dumps(payload))
        response.status_code = cls.status_code
        response.headers['Content-Type'] = 'application/json'

        return response
