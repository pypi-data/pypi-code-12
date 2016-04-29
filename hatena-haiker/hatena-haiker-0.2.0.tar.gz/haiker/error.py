#!/usr/bin/env python3
# coding: utf-8


class HaikerError(Exception):
    '''Raised when something goes wrong around this library.
    '''


class UnexpectedResponse(HaikerError):
    '''Raised when HTTP response is unexpected.
    '''

    def __init__(self, res):
        self._res = res

    def __str__(self):
        code = self.res.status_code
        text = self.res.text.replace('\n', ' ')
        if len(text) > 50:
            text = '{0}...'.format(text[:47])
        return '[{0}] {1}'.format(code, text)

    @property
    def res(self):
        '''response data'''
        return self._res
