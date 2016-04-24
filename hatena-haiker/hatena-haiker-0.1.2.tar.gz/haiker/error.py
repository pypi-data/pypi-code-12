#!/usr/bin/env python3
# coding: utf-8


class HaikerError(Exception):
    '''Raised when there is something wrong around this library.
    '''


class UnexpectedResponse(HaikerError):
    '''Raised when HTTP response is unexpected.
    A attribute ``res`` is the response object.
    '''

    def __init__(self, res):
        self.res = res

    def __str__(self):
        code = self.res.status_code
        text = self.res.text.replace('\n', ' ')
        if len(text) > 50:
            text = '{0}...'.format(text[:47])
        return '[{0}] {1}'.format(code, text)
