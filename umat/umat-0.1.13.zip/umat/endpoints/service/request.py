# -*- coding: utf-8 -*-
from requests import get
from six import reraise
from sys import exc_info
from .util import (
    print_bold,
    retry
)


class MatRequestError(Exception):
    pass


@retry(10)
def request(*args, **kwargs):
    response = get(*args, **kwargs)
    if __debug__:
        print_bold('Request URL: {}'.format(response.url))

    if __debug__ and response.status_code == 422:
        response_json = response.json()
        for error in response_json['errors']:
            print_bold(error['message'])

    if response.status_code != 200:
        raise MatRequestError(
            'Failed: HTTP status code is {}'.format(response.status_code)
        )

    response_json = response.json()

    if 'status_code' in response_json and response_json['status_code'] != 200:
        raise MatRequestError(
            'Failed: MAT status code is {}'.format(response_json['status_code'])
        )

    return response_json
