#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

from pyconclas.exceptions.client_exceptions import ConclasHTTPError

class Requester(object):

    def post(self, url, data, use_ssl, headers, timeout):
        """
            Definition:
                Executes a request post

            Returns:
                Returns a request result object
        """
        self._url = url
        self._data = data
        self._use_ssl = use_ssl
        self._headers = headers
        self._timeout = timeout

        try:
            return requests.post(
                self._url, data = self._data,
                verify = self._use_ssl,
                headers = self._headers,
                timeout = self._timeout)
        except requests.ConnectionError as e:
            raise ConclasHTTPError(e)
        except requests.Timeout as e:
            raise ConclasHTTPError(e)
