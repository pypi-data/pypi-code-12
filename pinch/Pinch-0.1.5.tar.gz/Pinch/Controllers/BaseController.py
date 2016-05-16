# -*- coding: utf-8 -*-

"""
   Pinch

   This file was automatically generated for Pinch by APIMATIC BETA v2.0 on 05/13/2016
"""

from Pinch.Http.RequestsClient import *
from Pinch.APIException import APIException

class BaseController(object):

    """All controllers inherit from this base class. It manages shared HTTP clients and global API errors."""

    http_client = RequestsClient()

    def __init__(self, client):
        if client != None:
            self.http_client = client

    def validate_response(self, response):
        if response.status_code == 401:
            raise APIException("Your API key is incorrect", response.status_code, response.raw_body)
        elif response.status_code == 400:
            raise APIException("There is an error in the parameters you send", response.status_code, response.raw_body)
        elif response.status_code == 404:
            raise APIException("Cannot find the resource specified", response.status_code, response.raw_body)
        elif (response.status_code < 200) or (response.status_code > 206): #[200,206] = HTTP OK
            raise APIException("HTTP Response Not OK", response.status_code, response.raw_body)
