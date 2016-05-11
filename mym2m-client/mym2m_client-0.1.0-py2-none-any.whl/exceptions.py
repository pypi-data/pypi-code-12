#!/usr/bin/env python


class ApiException(Exception):
    """
    Represents an exception encountered while communicating with the API.
    """

    def __init__(self, message, error_number=-1):
        self.message = message
        self.error_number = error_number
