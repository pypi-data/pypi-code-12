# coding: utf8
from __future__ import unicode_literals
from api_star.decorators import annotate
from api_star.exceptions import BadRequest
from api_star.utils import parse_header_params
from werkzeug.formparser import MultiPartParser as WerkzeugMultiPartParser
from werkzeug.formparser import default_stream_factory
from werkzeug.urls import url_decode_stream
import json


def json_parser():
    errors = {
        'malformed': 'Malformed JSON'
    }

    @annotate(media_type='application/json')
    def parser(stream, **context):
        data = stream.read().decode('utf-8')
        try:
            return json.loads(data)
        except ValueError:
            raise BadRequest(errors['malformed'])

    return parser


def multipart_parser():
    errors = {
        'missing-boundary-param': 'Multipart message missing boundary in Content-Type header',
        'malformed': 'Malformed multipart request'
    }

    @annotate(media_type='multipart/form-data')
    def parser(stream, **context):
        content_type = context['content_type']
        content_length = context['content_length']
        multipart_parser = WerkzeugMultiPartParser(default_stream_factory)

        params = parse_header_params(content_type)
        boundary = params.get('boundary')
        if boundary is None:
            raise BadRequest(errors['missing-boundary-param'])
        boundary = boundary.encode('ascii')

        try:
            data, files = multipart_parser.parse(stream, boundary, content_length)
        except ValueError:
            raise BadRequest(errors['malformed'])

        data.update(files)
        return data

    return parser


def urlencoded_parser():
    @annotate(media_type='application/x-www-form-urlencoded')
    def parser(stream, **context):
        return url_decode_stream(stream)
    return parser
