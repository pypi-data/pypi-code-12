from falcon import (
    HTTPError,
    HTTPNotAcceptable,
    HTTPUnsupportedMediaType,
    HTTPBadRequest
)
from falcon.status_codes import HTTP_753
import json


class MalformedJSONError(HTTPError):

    def __init__(self, description, **kwargs):
        super().__init__(HTTP_753, 'Malformed JSON', description, **kwargs)


class RequireJSON(object):

    def process_request(self, request, response):
        if not request.client_accepts_json:
            raise HTTPNotAcceptable('Can only send JSON responses.')

        if request.content_type is None and \
                (request.method != 'GET' and request.method != 'DELETE'):
            raise HTTPBadRequest('Incorrect header', 'No content type was provided')

        if request.method in ('POST', 'PUT') and \
                'application/json' not in request.content_type:
            raise HTTPUnsupportedMediaType('Request must be encoded as JSON.')


class JSONTranslator(object):

    def process_request(self, request, response):
        if request.content_length in (None, 0):
            return

        body = request.stream.read()
        if not body:
            raise HTTPBadRequest('Empty request body', 'A valid JSON document is required.')

        try:
            request.params.update(json.loads(body.decode('utf-8')))
        except (ValueError, UnicodeDecodeError):
            raise MalformedJSONError('Your request body is incorrect')
