# -*- coding: utf-8 -*-
import json
from io import BytesIO, BufferedReader
from urllib.parse import parse_qsl, urlencode
from wsgiref.util import request_uri
from watson.common.datastructures import ImmutableMultiDict
from watson.common.decorators import cached_property
from watson.common.imports import (get_qualified_name,
                                   load_definition_from_string)
from watson.http import STATUS_CODES, REQUEST_METHODS
from watson.http.cookies import CookieDict, cookies_from_environ
from watson.http.headers import (HeaderCollection,
                                 ServerCollection, fix_http_headers)
from watson.http.uri import Url
from watson.http.wsgi import copy_wsgi_input, get_form_vars, WSGI_BODY
from watson.http.sessions import COOKIE_KEY


class MessageMixin(object):

    """Base mixin for all Http Message objects.
    """
    _version = None

    @property
    def version(self):
        return self._version or '1.1'

    @version.setter
    def version(self, version):
        self._version = version


class Request(MessageMixin):
    """
    Provides a simple and usable interface for dealing with Http Requests.
    Requests are designed to be immutable and not altered after they are
    created, as such you should only set get/post/cookie etc attributes via
    the __init__.
    By default the session storage method is MemoryStorage which will store
    session in ram.

    See:
        - http://www.w3.org/Protocols/rfc2616/rfc2616-sec5.html
        - http://ken.coar.org/cgi/draft-coar-cgi-v11-03.txt

    Example:

    .. code-block:: python

        request = Request.from_environ(environ)
        print(request.method)
        print(request.post('my_post_var'))

        request = Request.from_dicts(server={'HTTP_METHOD': 'GET'}, get={'get_var': 'somevalue'})
        print(request.method) # get
        print(request.get('get_var')) # somevalue
    """

    _environ = None
    _session = None

    def __init__(self, environ):
        fix_http_headers(environ)
        self._environ = environ

    @property
    def environ(self):
        return self._environ

    @property
    def encoding(self):
        return self.headers.get_option('Content-Type', 'charset', 'utf-8')

    @property
    def raw_body(self):
        return self.environ[WSGI_BODY]

    @property
    def body(self):
        """Return the body of the request as a string.

        If unable to decode, return empty body.
        """
        copy_wsgi_input(self.environ)
        body = self.raw_body
        if isinstance(body, bytes):
            try:
                body = body.decode(self.encoding)
            except:
                body = ''
        return body

    @body.setter
    def body(self, body):
        """Set the body of the Request.

        Args:
            body (string|bytes): The body of the request.
        """
        if not isinstance(body, bytes):
            body = body.encode(self.encoding)
        self.environ[WSGI_BODY] = body

    @property
    def json_body(self):
        """Returns the body encoded as JSON.
        """
        return json.loads(self.body)

    @cached_property
    def method(self):
        """The method associated with the request.

        If the existing method is a POST, also check for HTTP_REQUEST_METHOD
        in the post vars to enable custom (but valid) request methods.

        Returns:
            A string representation of the Http Request method
        """
        method = self.environ.get('REQUEST_METHOD', 'GET').upper()
        if method == 'POST':
            post_method = self.post.get('HTTP_REQUEST_METHOD', method).upper()
            if post_method in REQUEST_METHODS:
                method = post_method
        return method

    @cached_property
    def url(self):
        """Generates a watson.http.uri.Url object based on Request.server
        variables.

        Example:

        .. code-block:: python

            request = ...
            print(request.url.path) # /

        Returns:
            A watson.http.uri.Url object
        """
        return Url(request_uri(self.environ))

    @cached_property
    def get(self):
        """A dict of all GET variables associated with the request.

        Returns:
            A dict of GET variables
        """
        qs = self.environ.get('QUERY_STRING', '')
        if qs:
            return ImmutableMultiDict(parse_qsl(qs, keep_blank_values=True))
        return ImmutableMultiDict()

    @cached_property
    def _get_post_files_from_environ(self):
        if self.environ.get('REQUEST_METHOD') not in ('POST', 'PUT', 'PATCH'):
            post = files = ImmutableMultiDict()
        else:
            copy_wsgi_input(self.environ)
            post, files = get_form_vars(self.environ, ImmutableMultiDict)
        return post, files

    @property
    def post(self):
        """A dict of all POST variables associated with the request.

        Returns:
            A dict of POST variables
        """
        post, files = self._get_post_files_from_environ
        return post

    @cached_property
    def files(self):
        """A dict of all files that have been uploaded as part of a
        enctype="multipart/form-data" request.

        Example:

        .. code-block:: python

            request = ...
            request.files['uploaded_file'] # FieldStorage object

        Returns:
            A dict of FieldStorage objects
        """
        post, files = self._get_post_files_from_environ
        return files

    @cached_property
    def headers(self):
        return HeaderCollection.from_environ(self.environ)

    @cached_property
    def server(self):
        return ServerCollection.from_environ(self.environ)

    @cached_property
    def cookies(self):
        """A dict of all cookies from the request.

        Example:

        .. code-block:: python

            request = ...
            request.cookies.get('test') # value of cookie named 'test'

        Returns:
            A watson.http.cookies.CookieDict object
        """
        return cookies_from_environ(self.environ)

    @property
    def session(self):
        session_class = self.environ.get('watson.session.class', None)
        if session_class and not self._session:
            storage = load_definition_from_string(session_class)
            options = self.environ['watson.session.options'].copy()
            http_cookie = self.environ.get('HTTP_COOKIE', None)
            if (http_cookie and '{0}='.format(COOKIE_KEY) in http_cookie):
                session_cookie = self.cookies[COOKIE_KEY]
                if session_cookie:
                    options['id'] = session_cookie.value
            self._session = storage(**options)
        return self._session

    # Initializers

    @classmethod
    def from_dict(cls,
                  method='GET',
                  get=None,
                  post=None,
                  server=None,
                  headers=None,
                  body=None,
                  encoding='utf-8',
                  session_class=None,
                  session_options=None):
        get = get or {}
        post = post or {}
        server = server or {}
        headers = headers or {}
        environ = {
            'REQUEST_METHOD': method,
            'QUERY_STRING': urlencode(get),
        }
        if post:
            body = urlencode(post)
            environ.update({
                'CONTENT_TYPE': 'application/x-www-form-urlencoded',
                'REQUEST_METHOD': 'POST',
                'wsgi.input': BufferedReader(BytesIO(body.encode(encoding)))
            })
        environ.update({
            'CONTENT_LENGTH': len(body) if body else 0
        })
        if 'wsgi.url_scheme' not in server:
            server['wsgi.url_scheme'] = 'http'
        if 'SERVER_NAME' not in server:
            server['SERVER_NAME'] = 'localhost'
        if 'SERVER_PORT' not in server:
            server['SERVER_PORT'] = '80'
        environ.update(server)
        environ.update(headers)
        return Request.from_environ(
            environ, session_class, session_options)

    @classmethod
    def from_environ(cls, environ,
                     session_class=None,
                     session_options=None):
        environ['watson.session.class'] = session_class
        environ['watson.session.options'] = session_options or {}
        request = cls(environ)
        return request

    # Convenience methods

    def is_method(self, *methods):
        """
        Determine whether or not a request was made via a specific method.

        Example:

        .. code-block:: python

            request = ... # request made via GET
            request.is_method('get') # True

        Args:
            method (string|list|tuple): the method or list of methods to check

        Returns:
            Boolean
        """
        methods = (methods,) if isinstance(methods, str) else methods
        return self.method in [m.upper() for m in methods]

    def is_xml_http_request(self):
        """
        Determine whether or not a request has originated via an XmlHttpRequest,
        assuming the relevant header has been set by the request.

        Returns:
            Boolean
        """
        return (self.headers.get(
            'X-Requested-With', '').lower() == 'xmlhttprequest')

    def is_secure(self):
        """
        Determine whether or not the request was made via Https.

        Returns:
            Boolean
        """
        if 'Https' in self.headers:
            return self.headers['Https'].lower() == 'https'
        return self.url.scheme.lower() == 'https'

    def host(self):
        """Determine the real host of a request.

        Returns:
            X_FORWARDED_FOR header variable if set, otherwise a watson.http.uri.Url
            hostname attribute.
        """
        return (
            self.url.hostname
            if 'X-Forwarded-For'
            not in self.headers
            else self.headers.get('X-Forwarded-For')
        )

    def __str__(self):
        return '{0} {1} HTTP/{2}\r\n{3}\r\n\r\n{4}'.format(self.method,
                                                           self.url,
                                                           self.version,
                                                           self.headers,
                                                           self.body)

    def __repr__(self):
        return '<{0} method:{1} url:{2}>'.format(get_qualified_name(self),
                                                 self.method,
                                                 self.url)


class Response(MessageMixin):

    """Provides a simple and usable interface for dealing with Http Responses.

    See:
        - http://www.w3.org/Protocols/rfc2616/rfc2616-sec6.html

    Example:

    .. code-block:: python

        def app(environ, start_response):
            response = Response(200, body='<h1>Hello World!</h1>')
            response.headers.add('Content-Type', 'text/html', charset='utf-8')
            response.cookies.add('something', 'test')
            start_response(*response.start())
            return [response()]
    """
    _status_code = None
    _cookies = None
    _body = None
    _prepared = False

    def __init__(self, status_code=None, headers=None, body=None, version=None):
        """
        Args:
            status_code (int): The status code for the Response
            headers (watson.http.headers.HeaderCollection): Valid response headers.
            body (string): The content for the response
            version (string): The Http version for the response
        """
        self.status_code = status_code
        self._headers = headers or HeaderCollection()
        if version:
            self.version = version
        if body:
            self.body = body

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, headers):
        if not isinstance(headers, HeaderCollection):
            headers = HeaderCollection(headers)
        self._headers = headers

    @property
    def raw_body(self):
        if self._body:
            return self._body
        return b''

    @property
    def body(self):
        """Returns the decoded body based on the response encoding type.
        """
        return self.raw_body.decode(self.encoding)

    @body.setter
    def body(self, body):
        """Set the body of the Request.

        Args:
            body (string): The body of the request.
        """
        self._body = body.encode(self.encoding)

    @property
    def status_code(self):
        """The status code for the Response.
        """
        return self._status_code or 200

    @status_code.setter
    def status_code(self, code):
        """
        Args:
            Code: an int representing the status code for the Response
        """
        self._status_code = code

    @property
    def status_line(self):
        """The formatted status line including the status code and message.
        """
        return (
            '{0} {1}'.format(
                self.status_code, STATUS_CODES.get(self.status_code)))

    @property
    def cookies(self):
        """Returns the cookies associated with the Response.
        """
        if not self._cookies:
            self.cookies = CookieDict()
        return self._cookies

    @cookies.setter
    def cookies(self, cookies):
        """Sets the cookies associated with the Response.

        Args:
            cookies (CookieDict): The cookies to add to the response.
        """
        self._cookies = cookies

    @property
    def encoding(self):
        """Retrieve the encoding for the response from the headers, defaults to
        UTF-8.
        """
        return self.headers.get_option('Content-Type', 'charset', 'utf-8')

    def start(self):
        """Return the status_line and headers of the response for use in a WSGI
        application.

        Returns:
            The status line and headers of the response.
        """
        self._prepare()
        return self.status_line, self.headers()

    def raw(self):
        """Return the raw encoded output for the response.
        """
        return str(self).encode(self.encoding)

    def __str__(self):
        self._prepare()
        return 'HTTP/{0} {1}\r\n{2}\r\n\r\n{3}'.format(self.version,
                                                       self.status_line,
                                                       self.headers,
                                                       self.body)

    def _prepare(self):
        if not self._prepared:
            if self._cookies:
                for cookie, morsel in self.cookies.items():
                    self.headers.add('Set-Cookie', str(morsel))
            self._prepared = True

    def __call__(self, start_response):
        """Execute the start_response method and return the response body.

        Args:
            start_response (callable): The start_response function from a WSGI
                                       callable.
        """
        start_response(*self.start())
        return [self.raw_body]
