import io
from api_star.compat import urlparse
from requests.adapters import BaseAdapter
from requests.models import Response
from requests.sessions import Session
from requests.structures import CaseInsensitiveDict
from requests.utils import get_encoding_from_headers
import sys


class Content(object):

    def __init__(self, content):
        self._len = len(content)
        self._read = 0
        self._bytes = io.BytesIO(content)

    def __len__(self):
        return self._len

    def read(self, amt=None):
        if amt:
            self._read += amt
        return self._bytes.read(amt)

    def stream(self, amt=None, decode_content=None):
        while self._read < self._len:
            yield self.read(amt)

    def release_conn(self):
        pass


class WSGIAdapter(BaseAdapter):
    def __init__(self, app):
        self.app = app

    def send(self, request, *args, **kwargs):
        urlinfo = urlparse(request.url)

        data = request.body.encode('utf-8') if request.body else b''

        environ = {
            'CONTENT_TYPE': request.headers.get('Content-Type'),
            'CONTENT_LENGTH': len(data),
            'QUERY_STRING': urlinfo.query,
            'PATH_INFO': urlinfo.path,
            'REQUEST_METHOD': request.method,
            'SERVER_NAME': urlinfo.hostname,
            'SERVER_PORT': urlinfo.port or ('443' if urlinfo.scheme == 'https' else '80'),
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': urlinfo.scheme,
            'wsgi.input': Content(data),
            'wsgi.errors': sys.stderr,
            'wsgi.multiprocess': False,
            'wsgi.multithread': False,
            'wsgi.run_once': False,
            'wsgi.url_scheme': urlinfo.scheme,
        }

        environ.update({
            'HTTP_{}'.format(name).replace('-', '_').upper(): value
            for name, value in request.headers.items()
        })

        response = Response()

        def start_response(status, headers):
            response.status_code = int(status.split(' ')[0])
            response.headers = CaseInsensitiveDict(headers)
            response.encoding = get_encoding_from_headers(response.headers)

        response.request = request
        response.url = request.url

        response.raw = Content(b''.join(self.app(environ, start_response)))

        return response

    def close(self):
        pass


class TestSession(Session):
    def __init__(self, app):
        super(TestSession, self).__init__()
        self.app = app
        self.mount('http://testserver', WSGIAdapter(app))

    def prepare_request(self, request):
        request.url = 'http://testserver/' + request.url.lstrip('/')
        return super(TestSession, self).prepare_request(request)
