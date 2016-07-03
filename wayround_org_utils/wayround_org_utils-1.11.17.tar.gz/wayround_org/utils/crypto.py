
"""
This module is not even developed yet
"""

# TODO: work!

import json


def encrypt_data(data, password):

    ret = None

    wrapper = {
        'data': data
        }

    try:
        ret = json.dumps(wrapper)
    except:
        ret = None

    return ret


def decrypt_data(data, password):

    ret = None

    try:
        ret = json.loads(data)
    except:
        ret = None
    else:
        ret = ret['data']

    return ret
