import six
import json
import logging

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from six.moves.urllib_parse import urlparse

from .errors import AppPlatformError
from datarobot.utils import get_endpoint, file_exists, to_api

logger = logging.getLogger(__package__)


class LogResponseMixin(object):
    log_hook = None

    def _log_response(self, response):
        if callable(self.log_hook):
            self.log_hook(response)  # pragma: no cover


class RESTClientObject(LogResponseMixin):
    """
    Parameters
        default_timeout
            timeout for http request and connection
        headers
            headers for outgoing requests
        log_hook
            optional callback for received request.Response
        log
            optional client logger
    """

    default_timeout = 60
    headers = {'content-type': 'application/json'}
    log_hook = None
    log = None
    endpoint = None
    auth = None
    token = None

    def __init__(self, auth, endpoint=None,
                 log=None, log_hook=None):
        self.endpoint = endpoint or get_endpoint()
        self.domain = '{}://{}'.format(urlparse(self.endpoint).scheme,
                                       urlparse(self.endpoint).netloc)
        self.log_hook = log_hook
        self.auth = auth
        self.log = log or logger
        self._make_auth_header()

    def _make_auth_header(self):
        if isinstance(self.auth, tuple):
            self.token = self._get_api_token()
        elif isinstance(self.auth, six.string_types):
            self.token = self.auth
        self.token_header = {'Authorization': 'Token {}'.format(self.token)}
        self.headers.update(self.token_header)

    def _get_api_token(self):
        payload = {"username": self.auth[0], "password": self.auth[1]}
        r = self.post(url="api_token/", data=payload)
        return r.json().get("apiToken")

    def _log_response(self, response):
        """
        Perform logging actions with the response object returned
        by Client using self.log_hook.
        """
        if callable(self.log_hook):
            self.log_hook(response)  # pragma: no cover

    def _join_endpoint(self, url):
        return '{}/{}'.format(self.endpoint, url)

    def _request(self, method, *args, **kwargs):
        response = requests.request(method, *args, **kwargs)
        try:
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError:
            self.log.exception('Error from datarobot api.')
            handle_http_error(response)  # TODO - response can be undef. here

    def request(self, method, *args, **kwargs):
        assert method in ('get', 'post', 'delete', 'patch', 'put')
        try:
            return self._request(method, *args, **kwargs)
        except Exception as e:
            raise AppPlatformError(e)

    def delete(self, url, timeout=None, **kwargs):
        url = self._join_endpoint(url)

        if timeout is not None:
            kwargs['timeout'] = timeout  # pragma: no cover

        response = self.request('delete', url, headers=self.headers, **kwargs)

        self._log_response(response)

        return response

    def get(self, url, params=None, timeout=None, join_endpoint=True, **kwargs):
        if join_endpoint:
            url = self._join_endpoint(url)
        kwargs['timeout'] = timeout or self.default_timeout
        response = self.request('get',
                                url,
                                headers=self.headers,
                                params=to_api(params),
                                **kwargs)

        self._log_response(response)

        return response

    def post(self, url, data=None, timeout=None, **kwargs):
        url = self._join_endpoint(url)
        kwargs['timeout'] = timeout or self.default_timeout
        if data:
            data = json.dumps(to_api(data))
        response = self.request('post',
                                url,
                                headers=self.headers,
                                data=data,
                                **kwargs)

        self._log_response(response)

        return response

    def patch(self, url, data=None, timeout=None, **kwargs):
        url = self._join_endpoint(url)
        kwargs['timeout'] = timeout or self.default_timeout
        if data:
            data = json.dumps(to_api(data))
        response = self.request('patch',
                                url,
                                headers=self.headers,
                                data=data,
                                **kwargs)

        self._log_response(response)

        return response

    def build_request(self, method, url, headers={}, join_endpoint=True,
                      add_token=True, **kwargs):
        if join_endpoint:
            url = self._join_endpoint(url)
        if add_token:
            headers.update(self.token_header)
        response = self.request(method,
                                url,
                                headers=headers,
                                **kwargs)
        self._log_response(response)
        return response

    def build_request_with_file(self, method, url,
                                fname,
                                form_data=None,
                                content=None,
                                file_path=None,
                                filelike=None):
        """Build request with a file that will use special
        MultipartEncoder instance (lazy load file).


        This method supports uploading a file on local disk, string content,
        or a file-like descriptor. ``fname`` is a required parameter, and
        only one of the other three parameters can be provided.

        Parameters
        ----------
        method : str.
            Method of request. This parameter is required, it can be
            'POST' or 'PUT' either 'PATCH'.
        url : str.
            Url that will be used it this request.
        fname : name of file
            This parameter is required, even when providing a file-like object
            or string content.
        content : str
            The content buffer of the file you would like to upload.
        file_path : str
            The path to a file on a local file system.
        filelike : file-like
            An open file descriptor to a file.

        Returns
        -------
        response : response object.

        """

        bad_args_msg = ('Upload should be used either with content buffer '
                        'or with path to file on local filesystem or with '
                        'open file descriptor')
        assert sum((bool(content),
                    bool(file_path),
                    bool(filelike))) == 1, bad_args_msg

        if file_path:
            if not file_exists(file_path):
                raise AppPlatformError(
                    'Provided file does not exists {}'.format(file_path))
            fields = {'file': (fname, open(file_path, 'rb'))}

        elif filelike:
            filelike.seek(0)
            fields = {'file': (fname, filelike)}
        else:
            if not isinstance(content, six.binary_type):
                raise AssertionError('bytes type required in content')
            fields = {'file': (fname, content)}

        form_data = form_data or {}
        data_for_encoder = to_api(form_data)
        data_for_encoder.update(fields)

        encoder = MultipartEncoder(fields=data_for_encoder)
        return self.build_request(method,
                                  url,
                                  headers={
                                      'Content-Type': encoder.content_type
                                  },
                                  data=encoder)

    def build_request_context(self, method, url, headers=None,
                              join_endpoint=True,
                              add_token=True):
        """Build a request context, which holds onto the method, url, and
        headers and can make multiple requests there
        """
        if headers is None:
            headers = {}
        if join_endpoint:
            url = self._join_endpoint(url)
        if add_token:
            headers.update(self.token_header)
        return RequestContext(method, url, headers, self.log_hook)


class RequestContext(LogResponseMixin):
    """Holds onto url and headers necessary to execute a request. Will be held
    by the entity that retries and does multithreading.

    """
    def __init__(self, method, url, headers, log_hook=None):
        self.method = method
        self.url = url
        self.headers = headers
        self.log_hook = log_hook

    def send_request(self, **kwargs):
        """"Send a request to the route this context is managing. If the
        response does not error, return the response
        """
        response = requests.request(self.method,
                                    self.url,
                                    headers=self.headers,
                                    **kwargs)
        self._log_response(response)
        try:
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError:
            handle_http_error(response)


def handle_http_error(response):
    if response.status_code < 500:
        template = '{} client error: {}'
    else:
        template = '{} server error: {}'
    if response.status_code == 401:
        message = template.format(response.status_code,
                                  'The server is saying you are not properly '
                                  'authenticated. Please make sure your API '
                                  'token is valid.')
    elif response.status_code == 403:
        message = template.format(response.status_code,
                                  'The server is saying that you do not have '
                                  'permissions to do the operation you '
                                  'requested, even though your API token is '
                                  'valid.')

    elif response.headers['content-type'] == 'application/json':
        data = response.json()
        error = data.get('Error') or data
        message = template.format(response.status_code,
                                  error)
    else:
        message = template.format(response.status_code,
                                  response.content.decode('ascii')[:79])
    raise AppPlatformError(message)
