# -*- coding: utf-8 -*-

import types

import requests

from .exceptions import InvalidStatusCodeError

HTTP_GET = 'GET'
HTTP_POST = 'POST'
HTTP_PATCH = 'PATCH'
HTTP_PUT = 'PUT'
HTTP_DELETE = 'DELETE'

VALID_METHODS = (
    HTTP_GET,
    HTTP_POST,
    HTTP_PATCH,
    HTTP_PUT,
    HTTP_DELETE
)

# Methods that require a unique ID to access
SINGLE_RESOURCE_METHODS = (
    HTTP_GET,
    HTTP_PUT,
    HTTP_PATCH,
    HTTP_DELETE,
)


class BaseClient(object):

    class Meta:
        # The base_url for the API of this client.
        base_url = NotImplemented
        # A list of registered resources.
        resources = NotImplemented

    def __init__(self, *args, **kwargs):
        self.assign_resources(self.Meta.resources)
        self.resources = self.Meta.resources
        self.session = requests.Session()

    def assign_resources(self, resource_class_list):
        """
        Given a tuple of Resource classes, parse their Meta.methods
        attributes and  client methods for communicating with those resources.

        Subclass this method to control how resources are assigned.
        """
        for resource in resource_class_list:
            self.assign_methods(resource)

    def assign_methods(self, resource_class):
        """
        Given a resource_class and it's Meta.methods tuple,
        assign methods for communicating with that resource.
        """
        assert all([
            x.upper() in VALID_METHODS for x in resource_class.Meta.methods])
        for method in resource_class.Meta.methods:

            self._assign_method(
                resource_class,
                method.upper()
            )

    def call_api(self, method_type, method_name, url,
                 valid_status_codes, resource, data,
                 uid, **kwargs):
        """
        Make HTTP calls.

        kwargs is a list of keyword arguments. Additional custom keyword
        arguments can be sent into this method and will be passed into
        subclass methods:

        - get_single_resource_url
        """

        if method_type in SINGLE_RESOURCE_METHODS and uid:
            url = resource.get_single_resource_url(
                url, uid, **kwargs)
        headers = {
            'X-CLIENT': self.Meta.name,
            'X-METHOD': method_name,
            'content-type': 'application/json'
        }
        params = {
            'headers': headers,
            'url': url
        }
        if method_type in ['POST', 'PUT', 'PATCH'] and isinstance(data, dict):
            params.update(json=data)
        prepared_request = self.session.prepare_request(
            requests.Request(method=method_type, **params)
        )
        response = self.session.send(prepared_request)
        return self._handle_response(response, valid_status_codes, resource)

    def _assign_method(self, resource_class, method_type):
        """
        Using reflection, assigns a new method to this class.
        """

        """
        If we assigned the same method to each method, it's the same
        method in memory, so we need one for each acceptable HTTP method.
        """

        method_name = '{}_{}'.format(
            method_type.lower(), resource_class.Meta.name.lower())
        url = resource_class.get_resource_url(
            resource_class, base_url=self.Meta.base_url
        )

        valid_status_codes = resource_class.Meta.acceptable_status_codes

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

    def _handle_response(self, response, valid_status_codes, resource):
        """
        Handles Response objects
        """
        if response.status_code not in valid_status_codes:
            raise InvalidStatusCodeError
        if response.content:
            data = response.json()
            if isinstance(data, list):
                return [resource(**x) for x in data]
            else:
                return [resource(**data)]
        return True
