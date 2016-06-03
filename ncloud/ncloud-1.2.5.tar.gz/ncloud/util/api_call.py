# ----------------------------------------------------------------------------
# Copyright 2015 Nervana Systems Inc.
# ----------------------------------------------------------------------------
"""
Helpers for making an API call
"""
from builtins import str
from collections import OrderedDict
import json
import logging
import requests
import sys

from ncloud.formatting.output import print_error

logger = logging.getLogger()


def print_debug(res):
    print("%r" % res.content)
    print("u%r" % res.text)
    print("%r" % res.encoding)
    print("%r" % res.headers)
    print("%r" % res.ok)
    print("%r" % res.reason)
    print("%r" % res.status_code)
    print('')


def api_call(config, endpoint, method="GET", data=None,
             params=None, files=None):
    url = config.api_url() + endpoint
    token = config.get_token(refresh=False)

    try:
        headers = {"X-Auth-Token": token}
        res = requests.request(method, url, data=data, params=params,
                               files=files, headers=headers)
        # print_debug(res)
        if res.status_code == 401:
            # token authentication failed, try to generate a new one and retry
            token = config.get_token(refresh=True)
            headers = {"X-Auth-Token": token}
            res = requests.request(method, url, data=data, params=params,
                                   files=files, headers=headers)
        elif not str(res.status_code).startswith('2'):
            print_error(res)
    except requests.exceptions.RequestException as re:
        logger.error(re)
        sys.exit(1)
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    if res is not None:
        content_type = res.headers['content-type']
        if content_type == 'application/json':
            return res.text
        else:
            # TODO: helium doesn't appear to set 'application/json' correctly
            if res.encoding:
                return res.content.decode(res.encoding)
            return res.content
    else:
        logger.error("No response received. Exiting.")
        sys.exit(1)


def api_call_json(config, endpoint, method="GET", data=None,
                  params=None, files=None):
    response = api_call(config, endpoint, method, data, params, files)
    return json.loads(response, object_pairs_hook=OrderedDict)
