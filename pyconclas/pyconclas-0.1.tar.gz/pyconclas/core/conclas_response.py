#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyconclas.exceptions.api_custom_exceptions import (
    InvalidTokenException, InvalidModeException, InvalidBodyException)


class ConclasResponse(object):
    def __init__(self, result, status_code, headers):
        self.status_code = status_code
        self.headers = headers
        self.result = result

    def _raise_error(self):
        """
            Definition:
                Find API error.
        """
        code_error = int(self.result['errors'][0]['code'])
        if code_error == 10:
            raise InvalidTokenException(
                "Missing token.")
        elif code_error == 11:
            raise InvalidTokenException(
                "Token format is invalid.")
        elif code_error == 12:
            raise InvalidTokenException(
                "Credentials are not correct.")
        elif code_error == 13:
            raise InvalidModeException(
                "Invalid mode request.")
        elif code_error == 14:
            raise InvalidBodyException(
                "Invalid Body Message.")
        elif code_error == 15:
            raise InvalidBodyException(
                "Invalid Body Json format.")
        else:
            raise Exception("Error not categorized.")

    def request_successful(self):
        """
            Returns:
                Returns true if request was successful
        """
        if 'errors' in self.result:
            self._raise_error()
        return True