"""
Common classes and functions (used throughout the package)
"""
import requests

from contextlib import closing
from bigpy import ensure_not_blank, trim, DotDict


def datetime_to_cloudhub_format(dt_utc):
    """
    Converts datetime or date to the format expected by CloudHub (for example, 2016-01-16T07:37:32.476Z).
    :param dt_utc: UTC datetime or date
    :return: string representation of the date and time in the format expected by CloudHub.
    """
    ms = dt_utc.microsecond if hasattr(dt_utc, 'microsecond') else 0
    return '{0:%Y-%m-%dT%H:%M:%S}.{1:0>3.0f}Z'.format(dt_utc, ms/1000.0)


class CloudHubError(Exception):
    """
    Root exception class for different exceptions raised in this package.
    """
    pass


class CloudHubApiError(CloudHubError):
    """
    Root of the exception hierarchy for communicating errors when interacting with CloudHub API.
    It carries the HTTP status code along with the message.
    """
    def __init__(self, message, status_code, append_status_code=True):
        message = '{0} (Status Code: {1})'.format(message, status_code) if append_status_code else message
        super(CloudHubApiError, self).__init__(message)
        self.status_code = status_code


class CloudHubNotFoundError(CloudHubApiError):
    """
    Raised in response to HTTP status 400 (Not Found).
    """
    DEFAULT_MESSAGE = '{0} ID [{1}] not found'

    def __init__(self, entity_id, message=None, status_code=400, entity_name='Entity', append_status_code=True):
        super(CloudHubNotFoundError, self).__init__(
                trim(message, self.DEFAULT_MESSAGE).format(entity_name, entity_id),
                status_code=status_code,
                append_status_code=append_status_code
        )
        self.entity_id = entity_id


class CloudHubUnauthorizedError(CloudHubApiError):
    """
    Raised in response to HTTP status 401 (Unauthorized).
    """
    DEFAULT_MESSAGE = 'Unauthorized: Access is denied due to invalid credentials'

    def __init__(self, message=DEFAULT_MESSAGE, status_code=401, append_status_code=True):
        super(CloudHubUnauthorizedError, self).__init__(message, status_code, append_status_code)


class CloudHubApi(object):
    """
    Base class for all components interacting with the CloudHub API
    """
    API_BASE_URL = 'https://anypoint.mulesoft.com/cloudhub/api'

    def __init__(self, user_name, password, api_base_url=None):
        """
        Initializes API handler class with the credentials and optional base URL to use. If no explicit base URL
        is specified, a default URL will be used.

        :param user_name: the user name to access CloudHub
        :param password: the password to access CloudHub
        :param api_base_url: the base URL to use for the API calls.
        """
        self.user_name = ensure_not_blank(user_name, 'The user name must not be blank')
        self.password = ensure_not_blank(password, 'The password must not be blank')

        api_base_url = trim(api_base_url)
        self.api_base_url = api_base_url if api_base_url else CloudHubApi.API_BASE_URL

        # remove trailing '/'
        self.api_base_url = self.api_base_url.strip('/')

    @staticmethod
    def _combine_path(base_url, path):
        base_url = trim(base_url).strip('/')
        path = trim(path).strip('/')
        return '{0}/{1}'.format(base_url, path) if path else base_url

    @staticmethod
    def _extract_error_description(response, default_message=None):
        try:
            parsed = response.json()
            if 'message' in parsed and parsed['message']:
                return parsed['message']
        except ValueError:
            return default_message if default_message else 'Unknown error occurred'

    @staticmethod
    def _handle_standard_errors(response, default_message=None):
        if response.status_code == 401:
            raise CloudHubUnauthorizedError()
        else:
            message = '{0} (Status code: {1})'.format(
                CloudHubApi._extract_error_description(response, default_message),
                response.status_code
            )
            raise CloudHubApiError(message, response.status_code)

    @staticmethod
    def _init_headers(headers=None, has_content=False):
        headers = dict(headers) if headers else {}
        if 'Accept' not in headers:
            headers['Accept'] = 'application/json'
        if has_content and 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
        return headers

    @property
    def _base_url(self):
        return self.api_base_url

    def _make_url(self, path):
        return self._combine_path(self._base_url, path)

    def _get(self, path=None, params=None, headers=None):
        headers = self._init_headers(headers, has_content=True)
        return requests.get(
                self._make_url(path),
                auth=(self.user_name, self.password),
                params=params,
                headers=headers
        )

    def _put(self, data, path=None, headers=None, **kwargs):
        headers = self._init_headers(headers, has_content=True)
        return requests.put(
                self._make_url(path),
                auth=(self.user_name, self.password),
                headers=headers,
                data=data,
                **kwargs
        )

    def _post(self, data, path=None, headers=None, **kwargs):
        headers = self._init_headers(headers, has_content=True)
        return requests.post(
                self._make_url(path),
                auth=(self.user_name, self.password),
                headers=headers,
                data=data,
                **kwargs
        )

    def _post_files(self, path, files):
        """
        Post just files, with no other payload - the regular post method is inconvenient as it attempts to
        "guess" the headers, which gets in a way here.

        :param path: the path relative to the base URL
        :param files: a dictionary with values being open files
        :return: response object representing an HTTP response
        """
        return requests.post(
                self._make_url(path),
                auth=(self.user_name, self.password),
                files=files
        )

    def _stream_to_file(self, target_file, path=None, params=None, headers=None, error_message=None):
        headers = self._init_headers(headers, has_content=True)
        with closing(
            requests.get(
                self._make_url(path),
                auth=(self.user_name, self.password),
                params=params,
                headers=headers,
                stream=True
            )
        ) as response:
            if response.status_code == 200:
                for chunk in response.iter_content(chunk_size=16384):
                    target_file.write(chunk)
            else:
                self._handle_standard_errors(response, error_message)

    def _load_single(self, path=None, error_message=None, params=None):
        response = self._get(path, params)
        if response.status_code == 200:
            return DotDict(response.json())
        else:
            self._handle_standard_errors(response, error_message)

    def _load_list(self, path, error_message=None):
        response = self._get(path)
        if response.status_code == 200:
            return [DotDict(x) for x in response.json()]
        else:
            self._handle_standard_errors(response, error_message)
