from urllib import quote

CODES = {
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    204: 'No Content',
    301: 'Moved Permanently',
    302: 'Found',
    304: 'Not Modified',
    307: 'Temporary Redirect',
    308: 'Permanent Redirect',
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    418: 'I\'m a teapot',  # super important
    429: 'Too Many Requests',
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
}

METHODS = [
    'GET',
    'POST',
    'PUT',
    'DELETE',
    'HEAD',
    'PATCH',
]


class Framework(object):
    def __init__(self, settings=None):
        self.routing = {verb: {} for verb in METHODS}
        if settings is None:
            settings = {}
        self.settings = settings

    def __call__(self, environ, start_response):
        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']
        func = self.lookup(path, method)

        request = {
            'method': method,
            'headers': {},
            'body': '',
            'path': path,
            'environ': environ,
            'routing': self.routing,
        }
        response = {
            'headers': {},
            'body': '',
        }
        if func is None:
            response_headers = response['headers'].items()
            start_response('404 Not Found', response_headers)
            yield 'Not Found'
            raise StopIteration()

        status_code = func(
            request=request,
            response=response,
            settings=self.settings,
        )

        if status_code is None:
            status_code = 200
        if 'Content-Type' not in response['headers']:
            response['headers']['Content-Type'] = 'text/plain'
        if 'Content-Length' not in response['headers']:
            response['headers']['Content-Length'] = str(len(response['body']))

        response_headers = response['headers'].items()

        start_response('{} {}'.format(status_code, CODES[status_code]), response_headers)
        yield response['body']

    def url_for(method, func):
        found_parts = _url_for(self.routing[method], func)
        for parts in found_parts:
            yield '/'.join(parts)

    def lookup(self, url, method):
        path, _, qs = url.partition('?')
        parts = path.strip('/').split('/') + ['']
        return _lookup(parts, self.routing[method])

    def route(self, url, func, methods=None):
        if methods is None:
            methods = METHODS
        parts = url.strip('/').split('/')
        try:
            for method in methods:
                _route(parts, self.routing[method], func)
        except ValueError as e:
            raise ValueError("Path defined twice {} ({})".format(
                url,
                e.message))

    def get(self, url, func):
        self.route(url, func, ['GET'])

    def post(self, url, func):
        self.route(url, func, ['POST'])

    def put(self, url, func):
        self.route(url, func, ['PUT'])

    def delete(self, url, func):
        self.route(url, func, ['DELETE'])


def _route(parts, table, func):
    val = table.get(parts[0])
    if len(parts) == 1:
        if isinstance(val, dict):
            table[parts[0]][''] = func
        elif val is None:
            table[parts[0]] = {'': func}
        else:
            raise ValueError("original: \"{}\" new: \"{}\"".format(
                val[''].__name__,
                func.__name__))
    else:
        if val is None:
            table[parts[0]] = {}
        _route(parts[1:], table[parts[0]], func)


def _lookup(parts, table):
    sub_table = table.get(parts[0], table.get('*'))
    if sub_table is None:
        return

    if not isinstance(sub_table, dict):
        return sub_table
    return _lookup(parts[1:], sub_table)


def reconstruct_url(environ):
    """ Written by Ian Bickling """
    url = environ['wsgi.url_scheme'] + '://'

    if environ.get('HTTP_HOST'):
        url += environ['HTTP_HOST']
    else:
        url += environ['SERVER_NAME']

        if environ['wsgi.url_scheme'] == 'https':
            if environ['SERVER_PORT'] != '443':
                url += ':' + environ['SERVER_PORT']
        else:
            if environ['SERVER_PORT'] != '80':
                url += ':' + environ['SERVER_PORT']

    url += quote(environ.get('SCRIPT_NAME', ''))
    url += quote(environ.get('PATH_INFO', ''))
    if environ.get('QUERY_STRING'):
        url += '?' + environ['QUERY_STRING']


def _url_for(routing, func):
    for key, value in routing.items():
        if value == func:
            yield [key]
        elif isinstance(value, dict):
            for found in _url_for(value, func):
                yield [key] + found
