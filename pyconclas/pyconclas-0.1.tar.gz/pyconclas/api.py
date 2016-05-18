#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests

from exceptions import client_exceptions

from core.conclas_response import ConclasResponse
from core.request import Requester

from utils.json_maker import JsonMaker, is_str_empty

BASE_URL = "http://localhost:5000/v1"


class ScorerType(object):
    DIRECT = "/categorise/direct/"
    INDIRECT = "/categorise/indirect/"


class Conclas(object):
    def __init__(self, token, timeout=5, use_ssl=True):
        """
            Params:
                ::token = Token to access API
                ::use_ssl = Define if the request uses verification SSL for
                            HTTPS requests. Defaults False.(Optional)
                ::timeout = Define timeout to request
        """
        if is_str_empty(token):
            raise client_exceptions.EmptyParameterException(
                    "The parameter 'token' needs a value")
        self._token = token
        self._use_ssl = use_ssl
        self._timeout = timeout
        self._requester = Requester()
        self.__status_code = None
        self.__headers = None
        self.__result = None

    @property
    def status_code(self):
        return self.__status_code

    @property
    def headers(self):
        return self.__headers

    @property
    def result(self):
        return self.__result

    def _check_api_args_method(
        self, contents,
        start_from_category=None,
        callback=None):

        if len(contents) == 0:
            raise client_exceptions.EmptyParameterException(
                 "The parameter 'contents' needs a value")

        if len(contents) > 1000:
            raise client_exceptions.DocMaxException(
                "The content size exceeded the limit")

        if start_from_category is not None:
            if is_str_empty(start_from_category):
                raise client_exceptions.EmptyParameterException(
                    "The parameter 'start_from_category' needs a value")

        if callback is not None:
            if is_str_empty(callback):
                raise client_exceptions.EmptyParameterException(
                    "The parameter 'callback' needs a value")



    def _make_request(self, json_data, url):
        """
            Returns:
                Returns a object request result
        """
        headers = {'Content-Type': 'application/json',
                    'Authorization': self._token}

        req = self._requester.post(
            url, data = json_data,
            use_ssl = self._use_ssl,
            headers = headers,
            timeout = self._timeout)

        if self._check_request(req):

            conclas_response = ConclasResponse(
                    result = json.loads(req.text),
                    status_code = req.status_code,
                    headers = req.headers)

            if conclas_response.request_successful():
                self._set_properties_values(conclas_response)

    def _check_request(self, request):
        """
            Params:
                ::request = A object request result

            Definition:
                Check if the request was successful

            Returns:
                Returns true if request was successful
        """
        if request.status_code is not requests.codes.ok:
            raise client_exceptions.ConclasHTTPError(
                "HTTP status code: {}".format(request.status_code))
        return True

    def _set_properties_values(self, conclas_response):
        """
            Params:
                ::request = A request object
            Definition:
                Populates status_code, headers and result properties with
                data from request
        """
        self.__status_code = conclas_response.status_code
        self.__headers = dict(conclas_response.headers)
        self.__result = conclas_response.result

    def direct_categorise(self, contents):
        """
            Params:
                ::contents = A content list

            Definition:
                Do direct categorise request

            Returns:
                Returns ConclasResponse object
        """
        self._check_api_args_method(contents)
        dict_data = {
            "contents": contents
        }
        url = BASE_URL + ScorerType.DIRECT
        json_final = JsonMaker(dict_data).get_json()
        self._make_request(json_final, url)

    def indirect_categorise(
        self, contents, callback):
        """
            Params:
                ::contents = A content list

            Definition:
                Do indirect categorise request

            Returns:
                Returns ConclasResponse object
        """
        self._check_api_args_method(contents, callback)
        dict_data = {
            "contents": contents,
            "callback": callback
        }
        json_final = JsonMaker(dict_data).get_json()
        url = BASE_URL + ScorerType.INDIRECT
        self._make_request(json_final, url)
