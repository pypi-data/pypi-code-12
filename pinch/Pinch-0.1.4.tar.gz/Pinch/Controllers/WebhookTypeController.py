# -*- coding: utf-8 -*-

"""
   Pinch.Controllers.WebhookTypeController

   This file was automatically generated for Pinch by APIMATIC BETA v2.0 on 05/13/2016
"""
from Pinch.APIHelper import APIHelper
from Pinch.APIException import APIException
from Pinch.Configuration import Configuration
from Pinch.Http.HttpRequest import HttpRequest
from Pinch.Http.HttpResponse import HttpResponse
from Pinch.Http.RequestsClient import RequestsClient
from Pinch.Controllers.BaseController import BaseController
from Pinch.CustomAuthUtility import CustomAuthUtility

from Pinch.Models.WebhookType import WebhookType


class WebhookTypeController(BaseController):

    """A Controller to access Endpoints in the Pinch API."""

    def __init__(self, http_client = None):
        """Constructor which allows a different HTTP client for this controller."""
        BaseController.__init__(self, http_client)

    def list(self):
        """Does a GET request to /webhook_types.

        List webhook types

        Returns:
            list of WebhookType: Response from the API. 

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # The base uri for api requests
        _query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        _query_builder += "/webhook_types"
        
        # Validate and preprocess url
        _query_url = APIHelper.clean_url(_query_builder)

        # Prepare headers
        _headers = {
            "user-agent": "APIMATIC 2.0",
            "accept": "application/json",
            "X-API-TOKEN": Configuration.x_api_token,
            "X-API-EMAIL": Configuration.x_api_email
        }

        # Prepare the API call.
        _http_request = self.http_client.get(_query_url, headers=_headers)

        #append custom auth authorization
        CustomAuthUtility.appendCustomAuthParams(_http_request)

        # Invoke the API call  to fetch the response.
        _response = self.http_client.execute_as_string(_http_request)

        # Global error handling using HTTP status codes.
        self.validate_response(_response)    

        # Try to convert response to JSON
        try:
            _response.raw_body = APIHelper.json_deserialize(_response.raw_body)
        except:
            pass
        
        # Try to cast response to list of desired type
        if isinstance(_response.raw_body, list):
            # Response is already in a list, return the list of objects 
            value = list()
            for item in _response.raw_body:
                try:
                    value.append(WebhookType.from_dictionary(item))
                except Exception:
                    raise APIException("Invalid JSON returned.", _response.status_code, _response.raw_body)
                    
            return value
