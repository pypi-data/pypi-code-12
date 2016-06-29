#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conclas.exceptions.api_custom_exceptions import (
    IncorrectCredentialsException,
    InvalidTokenException,
    InvalidModeException, 
    InvalidBodyFormatException,
    ApiLimitationException, 
    InvalidBodyMessageException, 
    MissingTokenException,
    PaymentRequiredException,
    BannedAccountException,
    AccountExceedFreeLimitException,
    LCoreUnsupportedLanguageException,
    LCoreInternalException,
    ContentTimeoutException)


class ConClasResponse(object):
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
        if code_error == 2:
            raise PaymentRequiredException(
                self.result['errors'][0]['message'])
        elif code_error == 3:
            raise BannedAccountException(
                self.result['errors'][0]['message'])
        elif code_error == 4:
            raise AccountExceedFreeLimitException(
                self.result['errors'][0]['message'])
        elif code_error == 10:
            raise MissingTokenException(
                self.result['errors'][0]['message'])
        elif code_error == 11:
            raise InvalidTokenException(
                self.result['errors'][0]['message'])
        elif code_error == 12:
            raise IncorrectCredentialsException(
                self.result['errors'][0]['message'])
        elif code_error == 13:
            raise InvalidModeException(
                self.result['errors'][0]['message'])
        elif code_error == 14:
            raise InvalidBodyMessageException(
                self.result['errors'][0]['message'])
        elif code_error == 15:
            raise InvalidBodyFormatException(
                self.result['errors'][0]['message'])
        elif code_error == 16:
            raise ApiLimitationException(
                self.result['errors'][0]['message'])
        elif code_error == 30:
            raise LCoreUnsupportedLanguageException(
                self.result['errors'][0]['message'])
        elif code_error == 31:
            raise LCoreInternalException(
                self.result['errors'][0]['message'])
        elif code_error == 32:
            raise ContentTimeoutException(
                self.result['errors'][0]['message'])
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