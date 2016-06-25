# -*- coding: utf-8 -*-

import types

import requests

from .constants import SINGLE_RESOURCE_METHODS, VALID_METHODS
from .exceptions import InvalidStatusCodeError


class HTTPClient(object):
    """
    HTTPClient has just the `call_api` method, so we can share this between
    various objects that require HTTP functionality
    """

    def prepare_http_request(self, method_type, params, **kwargs):
        """
        Prepares the HTTP REQUEST and returns it.

        Args:
            method_type: The HTTP method type
            params: Additional parameters for the HTTP request.
            kwargs: Any extra keyword arguements passed into a client method.

        returns:
            prepared_request: An HTTP request object.
        """
        prepared_request = self.session.prepare_request(
            requests.Request(method=method_type, **params)
        )
        return prepared_request

    def get_http_headers(self, client_name, method_name, **kwargs):
        """
        Prepares the HTTP HEADERS and returns them.

        Args:
            client_name: The name of the HTTP client
            method_name: The method name triggering this HTTP request.
            kwargs: Any extra keyword arguements passed into a client method.

        returns:
            headers: A dictionary of HTTP headers
        """
        headers = {
            'X-CLIENT': client_name,
            'X-METHOD': method_name,
            'content-type': 'application/json'
        }
        return headers

    def call_api(self, method_type, method_name, url,
                 valid_status_codes, resource, data,
                 uid, **kwargs):
        """
        Make HTTP calls.

        Args:
            method_type: The HTTP method
            method_name: The name of the python method making the HTTP call
            url: The full URL of the HTTP call
            valid_status_codes: A tuple of integer status codes
                                deemed acceptable as response statuses
            resource: The resource class that will be generated
            data: The post data being sent.
            uid: The unique identifier of the resource.
        Returns:

        kwargs is a list of keyword arguments. Additional custom keyword
        arguments can be sent into this method and will be passed into
        subclass methods:

        - get_single_resource_url
        - prepare_http_request
        - get_http_headers
        """

        if method_type in SINGLE_RESOURCE_METHODS:
            url = resource.get_single_resource_url(
                url=url, uid=uid, **kwargs)
        params = {
            'headers': self.get_http_headers(
                self.Meta.name, method_name, **kwargs),
            'url': url
        }
        if method_type in ['POST', 'PUT', 'PATCH'] and isinstance(data, dict):
            params.update(json=data)
        prepared_request = self.prepare_http_request(
            method_type, params, **kwargs)
        response = self.session.send(prepared_request)
        return self._handle_response(response, valid_status_codes, resource)

    def _handle_response(self, response, valid_status_codes, resource):
        """
        Handles Response objects

        Args:
            response: An HTTP reponse object
            valid_status_codes: A tuple list of valid status codes
            resource: The resource class to build from this response

        returns:
            resources: A list of Resource instances
        """
        if response.status_code not in valid_status_codes:
            raise InvalidStatusCodeError(
                'Recieved status code: {}, expected: {}'.format(
                    response.status_code, valid_status_codes
                    )
                )
        if response.content:
            data = response.json()
            if isinstance(data, list):
                # A list of results is always rendered
                return [resource(**x) for x in data]
            else:
                # Try and find the paginated resources
                key = resource.Meta.pagination_key
                if isinstance(data.get(key), list):
                    # Only return the paginated responses
                    return [resource(**x) for x in data.get(key)]
                else:
                    # Attempt to render this whole response as a resource
                    return [resource(**data)]
        return []


class BaseClient(HTTPClient):

    class Meta:
        # The name of this client API
        name = NotImplemented
        # The base_url for the API of this client.
        base_url = NotImplemented
        # A list of registered resources.
        resources = NotImplemented

    def __init__(self, *args, **kwargs):
        super(BaseClient, self).__init__(*args, **kwargs)
        self.assign_resources(self.Meta.resources)
        self.resources = self.Meta.resources
        self.session = requests.Session()

    def assign_resources(self, resource_class_list):
        """
        Given a tuple of Resource classes, parse their Meta.methods
        attributes and  client methods for communicating with those resources.

        Subclass this method to control how resources are assigned.

        Args:
            resource_class_list: A tuple of Resource classes
        """
        for resource in resource_class_list:
            self.assign_methods(resource)

    def assign_methods(self, resource_class):
        """
        Given a resource_class and it's Meta.methods tuple,
        assign methods for communicating with that resource.

        Args:
            resource_class: A single resource class
        """
        assert all([
            x.upper() in VALID_METHODS for x in resource_class.Meta.methods])
        for method in resource_class.Meta.methods:

            self._assign_method(
                resource_class,
                method.upper()
            )

    def _assign_method(self, resource_class, method_type):
        """
        Using reflection, assigns a new method to this class.

        Args:
            resource_class: A resource class
            method_type: The HTTP method type
        """

        """
        If we assigned the same method to each method, it's the same
        method in memory, so we need one for each acceptable HTTP method.
        """
        method_name = resource_class.get_method_name(
            resource_class, method_type)
        url = resource_class.get_resource_url(
            resource_class, base_url=self.Meta.base_url
        )
        valid_status_codes = resource_class.Meta.valid_status_codes

        # I know what you're going to say, and I'd love help making this nicer
        # reflection assigns the same memory addr to each method otherwise.
        def get(self, method_type=method_type, method_name=method_name,
                url=url, valid_status_codes=valid_status_codes,
                resource=resource_class, data=None, uid=None, **kwargs):
            return self.call_api(
                method_type, method_name,
                url, valid_status_codes, resource,
                data, uid=uid, **kwargs)

        def put(self, method_type=method_type, method_name=method_name,
                url=url, valid_status_codes=valid_status_codes,
                resource=resource_class, data=None, uid=None, **kwargs):
            return self.call_api(
                method_type, method_name,
                url, valid_status_codes, resource,
                data, uid=uid, **kwargs)

        def post(self, method_type=method_type, method_name=method_name,
                 url=url, valid_status_codes=valid_status_codes,
                 resource=resource_class, data=None, uid=None, **kwargs):
            return self.call_api(
                method_type, method_name,
                url, valid_status_codes, resource,
                data, uid=uid, **kwargs)

        def patch(self, method_type=method_type, method_name=method_name,
                  url=url, valid_status_codes=valid_status_codes,
                  resource=resource_class, data=None, uid=None, **kwargs):
            return self.call_api(
                method_type, method_name,
                url, valid_status_codes, resource,
                data, uid=uid, **kwargs)

        def delete(self, method_type=method_type, method_name=method_name,
                   url=url, valid_status_codes=valid_status_codes,
                   resource=resource_class, data=None, uid=None, **kwargs):
            return self.call_api(
                method_type, method_name,
                url, valid_status_codes, resource,
                data, uid=uid, **kwargs)

        method_map = {
            'GET': get,
            'PUT': put,
            'POST': post,
            'PATCH': patch,
            'DELETE': delete
        }

        setattr(
            self, method_name,
            types.MethodType(method_map[method_type], self)
        )
