from distutils.util import strtobool
from constants import (
    PENTAHO_DEFAULT_COOKIE_NAME,
    PENTAHO_AVAILABLE_ENDPOINT_TYPE
)
from users_api import PentahoUsersAPI
from roles_api import PentahoRolesAPI
import requests
import urlparse


class PentahoAuth(object):

    def get_auth_kwarg(self):
        raise NotImplementedError()


class PentahoBasicAuth(PentahoAuth):

    def __init__(self, username, password):
        self._username = username
        self._password = password

    def get_auth_kwarg(self):
        return {'auth': (self._username, self._password)}


class PentahoCookieAuth(PentahoAuth):

    def __init__(self, cookie_value, cookie_name=PENTAHO_DEFAULT_COOKIE_NAME):
        self._cookie_name = cookie_name
        self._cookie_value = cookie_value

    def get_auth_kwarg(self):
        return {'cookies': {self._cookie_name: self._cookie_value}}


class Pentaho(object):

    def __init__(self, pentaho_base_url="http://localhost", pentaho_auth_method=None, ssl_check=True):
        self.pentaho_base_url = pentaho_base_url
        self.do_ssl_check = ssl_check if type(ssl_check) is bool else strtobool(ssl_check)
        self.pentaho_auth_method = pentaho_auth_method
        self.users = PentahoUsersAPI(self)
        self.roles = PentahoRolesAPI(self)

    def set_auth_method(self, pentaho_auth_method):
        self.pentaho_auth_method = pentaho_auth_method

    def set_pentaho_base_url(self, pentaho_base_url):
        self.pentaho_base_url = pentaho_base_url

    def set_ssl_check(self, ssl_check):
        self.do_ssl_check = ssl_check

    @staticmethod
    def validate_urls(url):
        """
        Validate a url
        :param url: the url to validate
        :return: True if valid, False otherwise
        """
        valid = False
        parsed_url = urlparse.urlparse(url)
        if parsed_url:
            valid = True
        return valid

    def get_auth_kwarg(self):
        """
        return authentication parameters for requests object
        :return: dict containing authentication parameters
        """
        if self.pentaho_auth_method:
            return self.pentaho_auth_method.get_auth_kwarg()
        return {}

    def make_call(self, endpoint_type, endpoint, **kwargs):
        """
        Call Pentaho REST endpoint
        :param endpoint_type: type of endpoint to call (users, roles, etc...)
        :param endpoint: which endpoint to call (list, create, etc...)
        :param kwargs: parameters for the requests
        :return Response object from pentaho
        """
        kwargs.update(**self.get_auth_kwarg())
        if endpoint_type not in PENTAHO_AVAILABLE_ENDPOINT_TYPE:
            raise ValueError("[ERROR] api endpoint type %s does not exist" % endpoint_type)
        method, url = self.get_endpoint_method_url(PENTAHO_AVAILABLE_ENDPOINT_TYPE[endpoint_type], endpoint)
        return requests.request(method, url, verify=self.do_ssl_check, **kwargs)

    def get_endpoint_method_url(self, type, endpoint):
        """
        Generate based url
        :param endpoint: the type of endpoint required
        :param type: the type api
        :return: (method, url)
        """
        if not endpoint or endpoint not in type:
            raise ValueError("[ERROR] get_endpoint_method_url::endpoint_type improper definition... ")
        endpoint_method, endpoint_url = type[endpoint]
        pentaho_endpoint = urlparse.urljoin(self.pentaho_base_url, endpoint_url)
        if not self.validate_urls(pentaho_endpoint):
            raise ValueError("[ERROR] Improper endpoint :: {} ... ".format(pentaho_endpoint))
        return endpoint_method, pentaho_endpoint
