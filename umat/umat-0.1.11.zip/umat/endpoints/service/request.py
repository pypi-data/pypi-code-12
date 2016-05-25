# -*- coding: utf-8 -*-
from requests import get
from six import reraise
from sys import exc_info
from .util import print_bold


class MatRequestError(Exception):
    pass


def _request(*args, **kwargs):
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


def request(*args, **kwargs):
    lives = 5
    while lives:
        lives -= 1
        try:
            return _request(*args, **kwargs)
        except MatRequestError:
            info = exc_info()
            if __debug__:
                print_bold(info[1])
            if not lives:
                reraise(*info)
