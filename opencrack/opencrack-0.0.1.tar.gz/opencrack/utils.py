import json
import requests


def api_request(url, token_id, data=None,
                method='POST', content_type='application/json'):
    """Manual Openstack API wrapper since some of the clients suck, and can't
    do what we want them to.

    Args:
        url (string) - full path for the request
        token_id (string) - The token ID to use, will re-auth through keystone.
        data (dict) - A dict of data that will get JSON dumped. if None is
                      passed, it's dropped completely.
        method (string) - HTTP Method, GET | POST | PUT | DELETE

    Returns (requests.Response)
    """

    headers = {
        'content-type': content_type
    }

    if token_id:
        headers['X-Auth-Token'] = token_id

    if data:
        if content_type == 'application/json':
            data = json.dumps(data)
        resp = requests.request(method, url, headers=headers,
                                data=data)
    else:
        resp = requests.request(method, url, headers=headers)

    return resp


def is_otp_scoped(token):
    try:
        return 'OS-OTP' in token
    except (TypeError, KeyError):
        return False


def scope_catalog_to_region(catalog, region=None):
    """ Returns service catalog with endpoints in specified region """
    if not region:
        return catalog

    new_catalog = []

    for service in catalog:
        new_service = service.copy()
        new_service['endpoints'] = []
        for endpoint in service['endpoints']:
            if endpoint['region'] == region:
                new_service['endpoints'].append(endpoint)

        new_catalog.append(new_service)

    return new_catalog
