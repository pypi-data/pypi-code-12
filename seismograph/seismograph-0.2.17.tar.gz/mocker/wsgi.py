# -*- coding: utf-8 -*-

from wsgiref.simple_server import make_server

# from . import http


DEFAULT_STATUS = 500


HTTP_STATUS_TO_STRING = {
    100: 'Continue',
    101: 'Switching Protocols',
    102: 'Processing',
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non-Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',
    207: 'Multi-Status',
    226: 'IM Used',
    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Moved Temporarily',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    306: 'Switch Proxy',
    307: 'Temporary Redirect',
    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Request Entity Too Large',
    414: 'Request-URI Too Large',
    415: 'Unsupported Media Type',
    416: 'Requested Range Not Satisfiable',
    417: 'Expectation Failed',
    422: 'Unprocessable Entity',
    423: 'Locked',
    424: 'Failed Dependency',
    425: 'Unordered Collection',
    426: 'Upgrade Required',
    428: 'Precondition Required',
    429: 'Too Many Requests',
    431: 'Request Header Fields Too Large',
    434: 'Requested host unavailable',
    444: 'No Response',
    449: 'Retry With',
    451: 'Unavailable For Legal Reasons',
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported',
    506: 'Variant Also Negotiates',
    507: 'Insufficient Storage',
    508: 'Loop Detected',
    509: 'Bandwidth Limit Exceeded',
    510: 'Not Extended',
    511: 'Network Authentication Required',
}


STATUS_CODES = [s for s in HTTP_STATUS_TO_STRING.keys()]


def format_status(code):
    return '{} {}'.format(code, HTTP_STATUS_TO_STRING[code])


def format_headers(headers):
    result = []

    for h in headers.items():
        result.append(h)

    return result


def get_route(environ):
    path_info = environ.get('PATH_INFO', '/')
    query_string = environ.get('QUERY_STRING')
    return '{}{}'.format(
        path_info,
        u'?{}'.format(query_string) if query_string else '',
    )


class WSGIHandler(object):

    __default_mock__ = None

    def __init__(self):
        self.handler_chain = {}

    def add_mock(self, mock):
        self.handler_chain[mock.route] = mock

    def __call__(self, environ, start_response):
        route = get_route(environ)
        mock = self.handler_chain.get(route, self.__default_mock__)

        status = format_status(mock.status)
        response_headers = format_headers(mock.headers)

        start_response(status, response_headers)
        return [mock.body]


httpd = make_server('', 8888, WSGIHandler())
httpd.serve_forever()
