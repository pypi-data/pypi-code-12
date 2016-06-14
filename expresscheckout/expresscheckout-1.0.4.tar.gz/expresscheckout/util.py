import config
import requests
import sys


def check_param(kwargs, string):
    for key,value in kwargs.iteritems():
        if key.startswith(string):
            return True
    return False


def get_arg(kwargs, param):
    if kwargs is None:
        return None
    elif param in kwargs:
        return kwargs[param]
    else:
        return None


def request(method, url, parameters):

    if config.environment == 'production':
        server = 'https://api.juspay.in'
    elif config.environment == 'sandbox':
        server = 'https://sandbox.juspay.in'
    else:
        raise Exception("environment variable can only be 'production' or 'sandbox'")
    # Wrapper for requests
    if method.upper() == 'GET':
        response = requests.get(server + url, headers=config.version, params=parameters, auth=(config.api_key, ''))
    else:
        response = requests.post(server + url, headers=config.version, data=parameters, auth=(config.api_key, ''))

    # Report error if response is not 200 ("OK")
    if response.status_code not in range(200, 299):
        sys.stderr.write('ERROR from %s: %d' % (response.url, response.status_code))
        response.raise_for_status()
    return response

'''
class list_response:

    def __init__(self, count, offset, total, list):

        self.offset = offset
        self.count = count
        self.total = total
        self.list = list
'''