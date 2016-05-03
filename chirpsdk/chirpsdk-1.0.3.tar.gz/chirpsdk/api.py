#------------------------------------------------------------------------
#
#  This file is part of the Chirp Python SDK.
#  For full information on usage and licensing, see http://chirp.io/
#
#  Copyright (c) 2011-2016, Asio Ltd.
#  All rights reserved.
#
#------------------------------------------------------------------------

"""
Handles connections to the Chirp API server.
"""

import logging
import requests
from uuid import getnode

from .util import is_valid_shortcode, is_valid_longcode
from .exceptions import (
    ChirpNetworkException,
    ChirpAuthenticationFailed,
    ChirpInvalidShortcodeException,
    ChirpInvalidLongcodeException,
)
from .constants import *

log = logging.getLogger(__name__)


def generate_device_id():
    """ Returns the mac address of the host as a valid device_id. """
    return '-'.join(('%012x' % getnode())[i:i+2] for i in range(0, 12, 2))


def check_valid_code(check, exc):
    def wrapped(func):
        def wrapper(cls, code, *args, **kwargs):
            if not check(code):
                raise exc()
            return func(cls, code, *args, **kwargs)
        return wrapper
    return wrapped
check_valid_shortcode = check_valid_code(is_valid_shortcode, ChirpInvalidShortcodeException)
check_valid_longcode = check_valid_code(is_valid_longcode, ChirpInvalidLongcodeException)


class API(object):
    access_token = ''

    def __init__(self, app_key, app_secret, api_host=None):
        self.api_host = api_host if api_host else API_HOST
        self.api_root = API_ENDPOINT_ROOT
        self.authenticate(app_key, app_secret)

    def _make_url(self, endpoint):
        """ Construct an absolute URL."""
        return 'https://{}{}{}'.format(self.api_host, self.api_root, endpoint)

    def _make_headers(self):
        """ Construct the header required by the API."""
        if not self.access_token:
            return {}
        return {
            'X-Auth-Token': self.access_token,
        }

    def get(self, endpoint, stream=False):
        """ Make a GET request to an endpoint URL (relative to /v1). """
        url = self._make_url(endpoint)
        headers = self._make_headers()
        response = requests.get(url, headers=headers, stream=stream)
        try:
            response = response.json()
        except ValueError:
            pass

        log.debug('Response: {}'.format(response))
        if 'error' in response:
            raise ChirpNetworkException('Invalid status code: {} - {}'.format(
                response['status'], response['description']))
        return response

    def post(self, endpoint, data):
        """ Make a POST request to a URL (relative to /v1). """
        url = self._make_url(endpoint)
        headers = self._make_headers()
        response = requests.post(url, json=data, headers=headers).json()
        log.debug('Response: {}'.format(response))
        if 'error' in response:
            raise ChirpNetworkException('Invalid status code: {} - {}'.format(
                response['status'], response['description']))
        return response

    # Authentication
    def authenticate(self, app_key, app_secret):
        data = {
            'app_key': app_key,
            'app_secret': app_secret,
            'device_id': generate_device_id(),
        }
        try:
            response = self.post(API_ENDPOINT_AUTHENTICATE, data)
        except ChirpNetworkException:
            raise ChirpAuthenticationFailed()
        self.access_token = response['access_token']

    # Create/query chirps
    @check_valid_shortcode
    def get_chirp(self, shortcode):
        """ Retrieves a chirp associated with a given shortcode.
        Returns the dictionary of JSON returned by the server. """
        return self.get('{}/{}'.format(API_ENDPOINT_CHIRP, shortcode))

    def create_chirp(self, payload):
        """ Creates a chirp based on the given dictionary payload.
        Returns the dictionary of JSON returned by the server. """
        data = {
            'data': payload,
        }
        return self.post(API_ENDPOINT_CHIRP, data)

    @check_valid_shortcode
    def save_wav(self, shortcode, filename):
        response = self.get('{}/{}.wav'.format(API_ENDPOINT_CHIRP, shortcode), stream=True)
        with open(filename, 'wb') as wav:
            for chunk in response.iter_content(1024):
                wav.write(chunk)
        return filename

    @check_valid_shortcode
    def encode(self, shortcode):
        """ Encodes a shortcode to a longcode. """
        endpoint = '{}/{}'.format(API_ENDPOINT_CHIRP_ENCODE, shortcode)
        return self.get(endpoint)

    @check_valid_longcode
    def decode(self, longcode):
        """ Decodes a longcode to a shortcode. """
        endpoint = '{}/{}'.format(API_ENDPOINT_CHIRP_DECODE, longcode)
        return self.get(endpoint)
