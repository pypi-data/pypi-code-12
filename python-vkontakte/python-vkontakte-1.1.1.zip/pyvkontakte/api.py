import functools
import logging

import requests

from pyvkontakte import auth
from pyvkontakte.errors import VkontakteApiError

__all__ = ['VkontakteApi']
logger = logging.getLogger(__name__)


class VkontakteApi(object):
    default_api_version = '5.50'
    api_version = default_api_version
    base_url = 'https://api.vk.com/method/'

    @classmethod
    def auth(cls, login, password, client_id, scope):
        """
        Shortcut function to pyvkontakte.auth

        :rtype: VkontakteApi
        """
        data = auth.auth(login, password, client_id, scope)
        return cls(data['access_token'])


    def __init__(self, access_token=None, v=None):
        self.access_token = access_token
        self.api_version = v or self.default_api_version

    def _params_encode(self, **kwargs):
        """
        Works *in place*

        :param dict params:
        :rtype: dict
        """
        for key, value in kwargs.items():
            if isinstance(value, (tuple, list, set)):
                kwargs[key] = ','.join(map(str, value))
        if self.access_token:
            kwargs.setdefault('access_token', self.access_token)
        kwargs.setdefault('v', self.api_version)
        return kwargs

    def call(self, method, **kwargs):
        """
        :raise VkontakteApiError:
        :param str method:
        :param dict kwargs:
        :return dict:
        """
        params = self._params_encode(**kwargs)
        url = self.base_url + method
        return self._make_request(url, params=params)

    def _make_request(self, url, **kwargs):
        """
        :rtype: dict
        """
        logger.info('Api call: %s %s', url, str(kwargs))
        try:
            response = requests.get(url, **kwargs)
        except:
            logger.exception('Exception while calling api: %s %s', url, str(kwargs))
            raise 
        logger.debug('Api response: %s', response.text)
        return self._handle_response(response)

    def _handle_response(self, response):
        """
        :param requests.Response response:
        :rtype: dict
        """
        response.raise_for_status()
        json = response.json()
        if 'error' in json:
            raise VkontakteApiError(json)
        return json['response']

    def __getattr__(self, method):
        """
        In general, it is a method name where dots replaced with underscores.

        VkontakteApi().users_get(user_ids=1)
        is a shortcut for
        VkontakteApi().call('users.get', user_ids=1)

        :param str method:
        """
        method = method.replace('_', '.')
        return functools.partial(self.call, method=method)
