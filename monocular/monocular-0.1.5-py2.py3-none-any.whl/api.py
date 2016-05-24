"""
This module is the interface between Monocular and the other SDK modules.
"""
import json
from datetime import datetime
import io

import requests
from PIL import Image

from monocular import config as config
from monocular import util as util

VALID_IMAGE_TYPES = [
    'image/png',
    'image/jpeg',
    'image/bmp'
]

ATTEMPT_LIMIT = 4


def send_request(method, url, data):
    """ Handles sending of the request using the 'requests' module."""
    headers = {}

    # Check for access tokens
    if has_access():
        headers = {
            'Authorization': 'Bearer ' + config.get('access_token')
        }

    files={}

    # Move image parameter to the files dictionary
    if 'image' in data:
        files={'image': data.get('image')}
        data.pop('image')

    method = method.upper()
    # Sent the request using the provided method
    if method == 'GET':
        response = requests.get(url, headers=headers, params=data)
    elif method == 'POST':
        if files:
            response = requests.post(url, headers=headers, files=files, data=data)
        else:
            response = requests.post(url, headers=headers, data=data)
    elif method == 'PUT':
        if files:
            response = requests.put(url, headers=headers, files=files, data=data)
        else:
            response = requests.put(url, headers=headers, data=data)
    elif method == 'DELETE':
        response = requests.delete(url, headers=headers, data=data)

    return response


def parse_response(response):
    """ Parses response from send_request """
    status = response.status_code

    # NOTE: Workaround as Response from an oauth call does not contain content type header
    content_type = ''

    if 'content-type' in response.headers:
        content_type = response.headers['content-type']

    # Validate the status and handle it if it is an error status
    if util.check_status(status):
        if content_type in VALID_IMAGE_TYPES:
            img = Image.open(io.BytesIO(response.content))
            return img
        else:
            data = json.loads(response.text)
            return data
    else:
        response.raise_for_status()


def get_access_token():
    """ Gets  oauth Access Token from from the server """
    client_id = config.get('client_id')
    client_secret = config.get('client_secret')
    refresh_token = config.get('refresh_token')

    method = 'POST'

    url = '{0}/oauth/token'.format(config.get('base_url'))

    # Use the refresh_token to get a new token if one is present.
    if refresh_token:
        params = {
            'grant_type': 'refresh_token',
            'scope': 'monocular',
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token
        }
    else:
        params = {
            'grant_type': 'client_credentials',
            'scope': 'monocular',
            'client_id': client_id,
            'client_secret': client_secret
        }

    res = send_request(method, url, params)
    data = parse_response(res)

    # Set relevant values in the config object for later use.
    config.set('access_token', data.get('access_token'))
    config.set('refresh_token', data.get('refresh_token'))
    config.set('expires_in', data.get('expires_in'))
    config.set('issued_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def __datetime(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

def has_access():
    """ Check if this has access to the API """
    access_token = config.get('access_token')
    expres_in = config.get('expires_in')
    issued_at = config.get('issued_at')

    if access_token == '':
        return False

    # Check for an expired Token
    delta = __datetime(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) - __datetime(issued_at)
    if int(delta.total_seconds()) >= int(expres_in):
        return False

    return True


def _execute(method, path, params):
    """ Executes the request and handles the response """
    if not method.upper() == 'GET':
        if not isinstance(params, dict):
            raise ValueError('Request parameters must be of type dict')

    if not path[0] == '/':
        path = '/' + path

    url = config.get('base_url') + path

    res = send_request(method, url, params)
    data = parse_response(res)

    return data


def request(method, path, params):
    count = ATTEMPT_LIMIT

    while count > -1:
        count = count - 1
        if has_access():
            return _execute(method, path, params)
        else:
            get_access_token()

    return ('Failed to get access token after {0} attempts'.format(str(ATTEMPT_LIMIT)))


def get(path, params):
    return request('GET', path, params)


def post(path, params):
    return request('POST', path, params)


def put(path, params):
    return request('PUT', path, params)


def delete(path, params):
    return request('DELETE', path, params)
