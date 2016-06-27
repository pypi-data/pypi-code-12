"""This module is not considered part of the public interface. As of 2.3, anything here
may change or be removed without warning."""

import platform
import os

import requests
import six
from requests_toolbelt.multipart.encoder import MultipartEncoder
from six.moves.urllib_parse import urlparse

from . import __version__
from .utils import to_api, get_endpoint
from . import errors


class RESTClientObject(requests.Session):
    """
    Parameters
        default_timeout
            timeout for http request and connection
        headers
            headers for outgoing requests
    """

    default_timeout = 60

    def __init__(self, auth=None, endpoint=None):
        super(RESTClientObject, self).__init__()
        # Note: As of 2.3, get_endpoint will be gone and we will make `endpoint` required
        self.endpoint = endpoint or get_endpoint()
        self.domain = '{}://{}'.format(urlparse(self.endpoint).scheme,
                                       urlparse(self.endpoint).netloc)
        self.token = auth
        self.user_agent_header = self._make_user_agent_header()
        self.headers.update(self.user_agent_header)
        self.token_header = {'Authorization': 'Token {}'.format(self.token)}
        self.headers.update(self.token_header)

    def _make_user_agent_header(self):
        client_str = 'DataRobotPythonClient/{}'.format(__version__)
        platform_str = '{} {} {}'.format(platform.system(), platform.release(), platform.machine())
        final_header = {'User-Agent': '{} ({})'.format(client_str, platform_str)}
        return final_header

    def _join_endpoint(self, url):
        return '{}/{}'.format(self.endpoint, url)

    def strip_endpoint(self, url):
        expected = '{}/'.format(self.endpoint)
        if not url.startswith(expected):
            raise ValueError('unexpected url format: {}'.format(url))
        return url.split(expected)[1]

    def request(self, method, url, join_endpoint=True, **kwargs):
        kwargs.setdefault('timeout', self.default_timeout)
        if join_endpoint:
            url = self._join_endpoint(url)
        response = super(RESTClientObject, self).request(method, url, **kwargs)
        if not response:
            handle_http_error(response)
        return response

    def get(self, url, params=None, **kwargs):
        return self.request('get', url, params=to_api(params), **kwargs)

    def post(self, url, data=None, **kwargs):
        if data:
            kwargs['json'] = to_api(data)
        return self.request('post', url, **kwargs)

    def patch(self, url, data=None, **kwargs):
        if data:
            kwargs['json'] = to_api(data)
        return self.request('patch', url, **kwargs)

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
            if not os.path.exists(file_path):
                raise ValueError(
                    'Provided file does not exist {}'.format(file_path))
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
        headers = {'Content-Type': encoder.content_type}
        return self.request(method, url, headers=headers, data=encoder)


def _http_message(response):
    if response.status_code == 401:
        message = ('The server is saying you are not properly '
                   'authenticated. Please make sure your API '
                   'token is valid.')
    elif response.status_code == 403:
        message = (
            'The server is saying that you do not have '
            'permissions to do the operation you '
            'requested, even though your API token is '
            'valid.')
    elif response.headers['content-type'] == 'application/json':
        message = response.json()
    else:
        message = response.content.decode('ascii')[:79]
    return message


def handle_http_error(response):
    message = _http_message(response)
    if 400 <= response.status_code < 500:
        template = '{} client error: {}'
        exc_message = template.format(response.status_code, message)
        raise errors.ClientError(exc_message, response.status_code)
    else:
        template = '{} server error: {}'
        exc_message = template.format(response.status_code, message)
        raise errors.ServerError(exc_message, response.status_code)
