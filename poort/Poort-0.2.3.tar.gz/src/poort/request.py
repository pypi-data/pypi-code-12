# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from .utils import FileStorage
from .utils import flatten_multidict
from werkzeug.formparser import parse_form_data
from werkzeug.http import parse_cookie
from werkzeug.urls import url_decode
import json


class Request(object):
    """A request wrapper.

    :param host: Hostname of the request.
    :param path: Request part of the URI.
    :param method: Request method (like GET, POST, PUT).
    :param ssl: Check if the request was made over HTTPS.
    :param ip_address: IPAddress of the remote user.
    :param accept_type: Accept header (eg. application/json).
    :param content_type: Content-Type header (eg. multipart/form-data).
    :param query: Query part of the URI (?foo=bar).
    :param form: Form part of the Request (foo=bar).
    :param files: Files part of the Request, removed from `form`.
    :param cookies: Cookies of the Request.
    :param json: JSON part of the Request (content_type is application/json).
    :param params: All params (query, form, files, cookies, json) combined.
    :param environ: The original environ.

    :type host: str
    :type path: str
    :type method: str
    :type ssl: bool
    :type ip_address: str | None
    :type accept_type: str
    :type content_type: str
    :type want_json: bool
    :type want_html: bool
    :type query: dict
    :type form: dict
    :type files: dict[str, poort.utils.FileStorage]
    :type cookies: dict
    :type json: dict | None
    :type params: dict
    :type environ: dict

    .. code-block:: python

        import poort

        def application(environ, start_response):
            request = poort.Request(environ)

            if request.path == '/':
                response = poort.Response('Hallo world!')
            else:
                response = poort.Response('Not found.', status_code=404)

            return response(request, start_response)

    """
    def __init__(self, environ):
        self.environ = environ

        self.host = environ.get('HTTP_HOST', 'localhost')
        self.path = environ.get('PATH_INFO', '/')
        self.method = environ.get('REQUEST_METHOD', 'GET')
        self.ssl = environ.get('HTTPS', False) is not False

        self.ip_address = environ.get('REMOTE_ADDR', None)

        self.accept_type = environ.get('HTTP_ACCEPT', '')
        self.content_type = environ.get('CONTENT_TYPE', '')

        self.want_json = 'application/json' in self.accept_type
        self.want_html = 'text/html' in self.accept_type

        if 'wsgi.input' in environ:
            stream, form, files = parse_form_data(environ)

            self.query = flatten_multidict(url_decode(
                environ.get('QUERY_STRING', '')))
            self.form = flatten_multidict(form)
            self.files = flatten_multidict(files, lambda v: len(v.filename),
                                           FileStorage.from_original)
        else:
            stream = None

            self.query = dict()
            self.form = dict()
            self.files = dict()

        self.cookies = parse_cookie(environ)

        if 'application/json' in self.content_type and stream:
            try:
                self.json = json.loads(stream.read().decode('utf-8'))
            except ValueError:
                self.json = None
        else:
            self.json = None

        self.params = dict()
        self.params.update(self.query)
        self.params.update(self.form)
        self.params.update(self.files)
        if self.json:
            self.params.update(self.json)

    def as_dict(self):
        """Return the full request as a dict

        :rtype: dict
        """
        return {
            'host': self.host,
            'path': self.path,
            'method': self.method,
            'ssl': self.ssl,

            'ip_address': self.ip_address,

            'accept_type': self.accept_type,
            'content_type': self.content_type,

            'want_json': self.want_json,
            'want_html': self.want_html,

            'query': self.query,
            'form': self.form,
            'files': self.files,
            'cookies': self.cookies,
            'json': self.json,

            'params': self.params,
        }

    def get_cookie(self, name, default=None):
        """Retrieve cookie from the request.

        This matches with the api of `poort.Response`, this provides
        `response.set_cookie` and `response.del_cookie`.

        :param name: Name of the cookie.
        :param default: Default when the cookie is not set.

        :type name: str
        :type default: str | None

        :rtype: str | None
        """
        return self.cookies.get(name, default)
