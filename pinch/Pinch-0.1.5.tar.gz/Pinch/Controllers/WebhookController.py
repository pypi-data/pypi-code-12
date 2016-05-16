# -*- coding: utf-8 -*-

"""
   Pinch.Controllers.WebhookController

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

from Pinch.Models.Webhook import Webhook


class WebhookController(BaseController):

    """A Controller to access Endpoints in the Pinch API."""

    def __init__(self, http_client = None):
        """Constructor which allows a different HTTP client for this controller."""
        BaseController.__init__(self, http_client)

    def list(self):
        """Does a GET request to /webhooks.

        List the webhooks of the current user

        Returns:
            list of Webhook: Response from the API. 

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # The base uri for api requests
        _query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        _query_builder += "/webhooks"
        
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
                    value.append(Webhook.from_dictionary(item))
                except Exception:
                    raise APIException("Invalid JSON returned.", _response.status_code, _response.raw_body)
                    
            return value

    def create(self,
                webhook):
        """Does a POST request to /webhooks.

        TODO: type endpoint description here.

        Args:
            webhook (Webhook): TODO: type description here. Example: 

        Returns:
            Webhook: Response from the API. 

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Validate required parameters
        if webhook == None:
            raise ValueError("Required parameter 'webhook' cannot be None.")

        # The base uri for api requests
        _query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        _query_builder += "/webhooks"
        
        # Validate and preprocess url
        _query_url = APIHelper.clean_url(_query_builder)

        # Prepare headers
        _headers = {
            "user-agent": "APIMATIC 2.0",
            "accept": "application/json",
            "content-type": "application/json; charset=utf-8",
            "X-API-TOKEN": Configuration.x_api_token,
            "X-API-EMAIL": Configuration.x_api_email
        }

        # Prepare the API call.
        _http_request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(webhook))

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

        # Try to cast response to desired type
        if isinstance(_response.raw_body, dict):
            # Response is already in a dictionary, return the object 
            try:
                return Webhook.from_dictionary(_response.raw_body)
            except Exception:
                raise APIException("Invalid JSON returned.", _response.status_code, _response.raw_body)

    def update(self,
                webhook_id,
                webhook = None):
        """Does a PUT request to /webhooks/{webhook_id}.

        TODO: type endpoint description here.

        Args:
            webhook_id (int): TODO: type description here. Example: 
            webhook (Webhook, optional): TODO: type description here. Example:
                
        Returns:
            Webhook: Response from the API. 

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Validate required parameters
        if webhook_id == None:
            raise ValueError("Required parameter 'webhook_id' cannot be None.")

        # The base uri for api requests
        _query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        _query_builder += "/webhooks/{webhook_id}"

        # Process optional template parameters
        _query_builder = APIHelper.append_url_with_template_parameters(_query_builder, { 
            "webhook_id": webhook_id
        })
        
        # Validate and preprocess url
        _query_url = APIHelper.clean_url(_query_builder)

        # Prepare headers
        _headers = {
            "user-agent": "APIMATIC 2.0",
            "accept": "application/json",
            "content-type": "application/json; charset=utf-8",
            "X-API-TOKEN": Configuration.x_api_token,
            "X-API-EMAIL": Configuration.x_api_email
        }

        # Prepare the API call.
        _http_request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(webhook))

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

        # Try to cast response to desired type
        if isinstance(_response.raw_body, dict):
            # Response is already in a dictionary, return the object 
            try:
                return Webhook.from_dictionary(_response.raw_body)
            except Exception:
                raise APIException("Invalid JSON returned.", _response.status_code, _response.raw_body)

    def destroy(self,
                webhook_id):
        """Does a DELETE request to /webhooks/{webhook_id}.

        TODO: type endpoint description here.

        Args:
            webhook_id (int): TODO: type description here. Example: 

        Returns:
            string: Response from the API. 

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Validate required parameters
        if webhook_id == None:
            raise ValueError("Required parameter 'webhook_id' cannot be None.")

        # The base uri for api requests
        _query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        _query_builder += "/webhooks/{webhook_id}"

        # Process optional template parameters
        _query_builder = APIHelper.append_url_with_template_parameters(_query_builder, { 
            "webhook_id": webhook_id
        })
        
        # Validate and preprocess url
        _query_url = APIHelper.clean_url(_query_builder)

        # Prepare headers
        _headers = {
            "user-agent": "APIMATIC 2.0",
            "X-API-TOKEN": Configuration.x_api_token,
            "X-API-EMAIL": Configuration.x_api_email
        }

        # Prepare the API call.
        _http_request = self.http_client.delete(_query_url, headers=_headers)

        #append custom auth authorization
        CustomAuthUtility.appendCustomAuthParams(_http_request)

        # Invoke the API call  to fetch the response.
        _response = self.http_client.execute_as_string(_http_request)

        # Global error handling using HTTP status codes.
        self.validate_response(_response)    

        # Return appropriate type
        return _response.raw_body



    def get(self,
                id):
        """Does a GET request to /webhooks/{id}.

        Get a specific webhook by its id

        Args:
            id (string): TODO: type description here. Example: 

        Returns:
            Webhook: Response from the API. 

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Validate required parameters
        if id == None:
            raise ValueError("Required parameter 'id' cannot be None.")

        # The base uri for api requests
        _query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        _query_builder += "/webhooks/{id}"

        # Process optional template parameters
        _query_builder = APIHelper.append_url_with_template_parameters(_query_builder, { 
            "id": id
        })
        
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

        # Try to cast response to desired type
        if isinstance(_response.raw_body, dict):
            # Response is already in a dictionary, return the object 
            try:
                return Webhook.from_dictionary(_response.raw_body)
            except Exception:
                raise APIException("Invalid JSON returned.", _response.status_code, _response.raw_body)
