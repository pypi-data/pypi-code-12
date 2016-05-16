# -*- coding: utf-8 -*-

"""
   Pinch.Controllers.TicketController

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

from Pinch.Models.Ticket import Ticket


class TicketController(BaseController):

    """A Controller to access Endpoints in the Pinch API."""

    def __init__(self, http_client = None):
        """Constructor which allows a different HTTP client for this controller."""
        BaseController.__init__(self, http_client)

    def list(self):
        """Does a GET request to /tickets.

        List all the opened tickets of every clients you are working for

        Returns:
            list of Ticket: Response from the API. 

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # The base uri for api requests
        _query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        _query_builder += "/tickets"
        
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
                    value.append(Ticket.from_dictionary(item))
                except Exception:
                    raise APIException("Invalid JSON returned.", _response.status_code, _response.raw_body)
                    
            return value

    def accept_intervention(self,
                            ticket_id):
        """Does a POST request to /tickets/{ticket_id}/accept.

        This method returns no result but the status code tells you if the
        operation succedded

        Args:
            ticket_id (string): TODO: type description here. Example: 

        Returns:
            Ticket: Response from the API. 

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Validate required parameters
        if ticket_id == None:
            raise ValueError("Required parameter 'ticket_id' cannot be None.")

        # The base uri for api requests
        _query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        _query_builder += "/tickets/{ticket_id}/accept"

        # Process optional template parameters
        _query_builder = APIHelper.append_url_with_template_parameters(_query_builder, { 
            "ticket_id": ticket_id
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
        _http_request = self.http_client.post(_query_url, headers=_headers)

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
                return Ticket.from_dictionary(_response.raw_body)
            except Exception:
                raise APIException("Invalid JSON returned.", _response.status_code, _response.raw_body)

    def set_intervention_date(self,
                              intervention_date,
                              ticket_id):
        """Does a POST request to /tickets/{ticket_id}/set_intervention_date.

        TODO: type endpoint description here.

        Args:
            intervention_date (DateTime): TODO: type description here.
                Example: 
            ticket_id (string): TODO: type description here. Example: 

        Returns:
            Ticket: Response from the API. 

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Validate required parameters
        if intervention_date == None:
            raise ValueError("Required parameter 'intervention_date' cannot be None.")
        elif ticket_id == None:
            raise ValueError("Required parameter 'ticket_id' cannot be None.")

        # The base uri for api requests
        _query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        _query_builder += "/tickets/{ticket_id}/set_intervention_date"

        # Process optional template parameters
        _query_builder = APIHelper.append_url_with_template_parameters(_query_builder, { 
            "ticket_id": ticket_id
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

        # Prepare form parameters
        _form_parameters = {
            "intervention_date": intervention_date
        }

        # Prepare the API call.
        _http_request = self.http_client.post(_query_url, headers=_headers, parameters=_form_parameters)

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
                return Ticket.from_dictionary(_response.raw_body)
            except Exception:
                raise APIException("Invalid JSON returned.", _response.status_code, _response.raw_body)

    def upload_quote(self,
                     file,
                     ticket_id):
        """Does a POST request to /tickets/{ticket_id}/quote_upload.

        TODO: type endpoint description here.

        Args:
            file (string): TODO: type description here. Example: 
            ticket_id (string): TODO: type description here. Example: 

        Returns:
            Ticket: Response from the API. 

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Validate required parameters
        if file == None:
            raise ValueError("Required parameter 'file' cannot be None.")
        elif ticket_id == None:
            raise ValueError("Required parameter 'ticket_id' cannot be None.")

        # The base uri for api requests
        _query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        _query_builder += "/tickets/{ticket_id}/quote_upload"

        # Process optional template parameters
        _query_builder = APIHelper.append_url_with_template_parameters(_query_builder, { 
            "ticket_id": ticket_id
        })

        _files = {
            "file": file

        }
        
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
        _http_request = self.http_client.post(_query_url, headers=_headers, files=_files)

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
                return Ticket.from_dictionary(_response.raw_body)
            except Exception:
                raise APIException("Invalid JSON returned.", _response.status_code, _response.raw_body)

    def send_message(self,
                     body,
                     ticket_id):
        """Does a POST request to /tickets/{ticket_id}/message.

        TODO: type endpoint description here.

        Args:
            body (string): TODO: type description here. Example: 
            ticket_id (string): TODO: type description here. Example: 

        Returns:
            Ticket: Response from the API. 

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Validate required parameters
        if body == None:
            raise ValueError("Required parameter 'body' cannot be None.")
        elif ticket_id == None:
            raise ValueError("Required parameter 'ticket_id' cannot be None.")

        # The base uri for api requests
        _query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        _query_builder += "/tickets/{ticket_id}/message"

        # Process optional template parameters
        _query_builder = APIHelper.append_url_with_template_parameters(_query_builder, { 
            "ticket_id": ticket_id
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

        # Prepare form parameters
        _form_parameters = {
            "body": body
        }

        # Prepare the API call.
        _http_request = self.http_client.post(_query_url, headers=_headers, parameters=_form_parameters)

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
                return Ticket.from_dictionary(_response.raw_body)
            except Exception:
                raise APIException("Invalid JSON returned.", _response.status_code, _response.raw_body)

    def declare_intervention_done(self,
                                  ticket_id,
                                  intervention_date = None):
        """Does a POST request to /tickets/{ticket_id}/intervention_done.

        TODO: type endpoint description here.

        Args:
            ticket_id (string): TODO: type description here. Example: 
            intervention_date (DateTime, optional): TODO: type description
                here. Example: 

        Returns:
            Ticket: Response from the API. 

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Validate required parameters
        if ticket_id == None:
            raise ValueError("Required parameter 'ticket_id' cannot be None.")

        # The base uri for api requests
        _query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        _query_builder += "/tickets/{ticket_id}/intervention_done"

        # Process optional template parameters
        _query_builder = APIHelper.append_url_with_template_parameters(_query_builder, { 
            "ticket_id": ticket_id
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

        # Prepare form parameters
        _form_parameters = {
            "intervention_date": intervention_date
        }

        # Prepare the API call.
        _http_request = self.http_client.post(_query_url, headers=_headers, parameters=_form_parameters)

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
                return Ticket.from_dictionary(_response.raw_body)
            except Exception:
                raise APIException("Invalid JSON returned.", _response.status_code, _response.raw_body)

    def upload_document(self,
                        file,
                        ticket_id):
        """Does a POST request to /tickets/{ticket_id}/document_upload.

        The document should not be an invoice nor a quote

        Args:
            file (string): TODO: type description here. Example: 
            ticket_id (string): TODO: type description here. Example: 

        Returns:
            Ticket: Response from the API. 

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Validate required parameters
        if file == None:
            raise ValueError("Required parameter 'file' cannot be None.")
        elif ticket_id == None:
            raise ValueError("Required parameter 'ticket_id' cannot be None.")

        # The base uri for api requests
        _query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        _query_builder += "/tickets/{ticket_id}/document_upload"

        # Process optional template parameters
        _query_builder = APIHelper.append_url_with_template_parameters(_query_builder, { 
            "ticket_id": ticket_id
        })

        _files = {
            "file": file

        }
        
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
        _http_request = self.http_client.post(_query_url, headers=_headers, files=_files)

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
                return Ticket.from_dictionary(_response.raw_body)
            except Exception:
                raise APIException("Invalid JSON returned.", _response.status_code, _response.raw_body)

    def upload_picture(self,
                       file,
                       ticket_id):
        """Does a POST request to /tickets/{ticket_id}/picture_upload.

        TODO: type endpoint description here.

        Args:
            file (string): TODO: type description here. Example: 
            ticket_id (string): TODO: type description here. Example: 

        Returns:
            Ticket: Response from the API. 

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Validate required parameters
        if file == None:
            raise ValueError("Required parameter 'file' cannot be None.")
        elif ticket_id == None:
            raise ValueError("Required parameter 'ticket_id' cannot be None.")

        # The base uri for api requests
        _query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        _query_builder += "/tickets/{ticket_id}/picture_upload"

        # Process optional template parameters
        _query_builder = APIHelper.append_url_with_template_parameters(_query_builder, { 
            "ticket_id": ticket_id
        })

        _files = {
            "file": file

        }
        
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
        _http_request = self.http_client.post(_query_url, headers=_headers, files=_files)

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
                return Ticket.from_dictionary(_response.raw_body)
            except Exception:
                raise APIException("Invalid JSON returned.", _response.status_code, _response.raw_body)

    def get(self,
                ticket_id):
        """Does a GET request to /tickets/{ticket_id}.

        TODO: type endpoint description here.

        Args:
            ticket_id (string): TODO: type description here. Example: 

        Returns:
            Ticket: Response from the API. 

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Validate required parameters
        if ticket_id == None:
            raise ValueError("Required parameter 'ticket_id' cannot be None.")

        # The base uri for api requests
        _query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        _query_builder += "/tickets/{ticket_id}"

        # Process optional template parameters
        _query_builder = APIHelper.append_url_with_template_parameters(_query_builder, { 
            "ticket_id": ticket_id
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
                return Ticket.from_dictionary(_response.raw_body)
            except Exception:
                raise APIException("Invalid JSON returned.", _response.status_code, _response.raw_body)

    def upload_invoice(self,
                       file,
                       ticket_id):
        """Does a POST request to /tickets/{ticket_id}/invoice_upload.

        TODO: type endpoint description here.

        Args:
            file (string): TODO: type description here. Example: 
            ticket_id (string): TODO: type description here. Example: 

        Returns:
            string: Response from the API. 

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Validate required parameters
        if file == None:
            raise ValueError("Required parameter 'file' cannot be None.")
        elif ticket_id == None:
            raise ValueError("Required parameter 'ticket_id' cannot be None.")

        # The base uri for api requests
        _query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        _query_builder += "/tickets/{ticket_id}/invoice_upload"

        # Process optional template parameters
        _query_builder = APIHelper.append_url_with_template_parameters(_query_builder, { 
            "ticket_id": ticket_id
        })

        _files = {
            "file": file

        }
        
        # Validate and preprocess url
        _query_url = APIHelper.clean_url(_query_builder)

        # Prepare headers
        _headers = {
            "user-agent": "APIMATIC 2.0",
            "X-API-TOKEN": Configuration.x_api_token,
            "X-API-EMAIL": Configuration.x_api_email
        }

        # Prepare the API call.
        _http_request = self.http_client.post(_query_url, headers=_headers, files=_files)

        #append custom auth authorization
        CustomAuthUtility.appendCustomAuthParams(_http_request)

        # Invoke the API call  to fetch the response.
        _response = self.http_client.execute_as_string(_http_request)

        # Global error handling using HTTP status codes.
        self.validate_response(_response)    

        # Return appropriate type
        return _response.raw_body


