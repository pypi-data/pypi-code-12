# -*- coding: utf-8 -*-

import sys
import types

import inflect

import requests

from .clients import HTTPClient
from .constants import DEFAULT_VALID_STATUS_CODES
from .exceptions import BadURLException, MissingUidException

if sys.version_info[0] == 3:
    # Py3
    from urllib.parse import urlparse
else:
    # Py2
    from urlparse import urlparse


class BaseResource(object):
    """
    A simple representation of a resource.

    Usage:

        from beckett.resources import BaseResource

        class Product(BaseResource):

            class Meta:
                name = 'Product'
                identifier = 'slug'
                attributes = (
                    'slug',
                    'name',
                    'price',
                    'discount'
                )

        # Data will usually come straight from the client method
        >>> data = {'name': 'Tasty product', 'slug': 'sluggy'}
        >>> product = Product(**data)
        <Product | sluggy>
        >>> product.name
        'Tasty product'

    """

    class Meta:
        # The name of this resource, used in __str__ methods.
        name = 'Resource'
        # The name of the resource used in the URL, i.e. 'resources'
        resource_name = None
        # The key with which you uniquely identify this resource.
        identifier = 'id'
        # Acceptable attributes that you want to display in this resource.
        attributes = (identifier,)
        # HTTP status codes that are considered "acceptable"
        # when calling this resource
        valid_status_codes = DEFAULT_VALID_STATUS_CODES
        # HTTP Methods that work on this resource
        methods = (
            'get',
        )
        # When receiving paginated results, use this key to render instances.
        pagination_key = 'results'

    def __init__(self, *args, **kwargs):
        self.set_attributes(**kwargs)

    def __str__(self):
        """
        Returns a string representation based on the `self.Meta.name`
        and `self.Meta.identifier` attribute value.
        """
        return '<{} | {}>'.format(
            self.Meta.name, getattr(self, self.Meta.identifier))

    def set_attributes(self, **kwargs):
        """
        Set the resource attributes from the kwargs.
        Only sets items in the `self.Meta.attributes` white list.

        Subclass this method to customise attributes.

        Args:
            kwargs: Keyword arguements passed into the init of this class
        """
        for field, value in kwargs.items():
            if field in self.Meta.attributes:
                setattr(self, field, value)

    @classmethod
    def get_resource_url(cls, resource, base_url):
        """
        Construct the URL for talking to this resource.

        i.e.:

        http://myapi.com/api/resource

        Note that this is NOT the method for calling individual instances i.e.

        http://myapi.com/api/resource/1

        Args:
            resource: The resource class instance
            base_url: The Base URL of this API service.
        returns:
            resource_url: The URL for this resource
        """
        if resource.Meta.resource_name:
            url = '{}/{}'.format(base_url, resource.Meta.resource_name)
        else:
            p = inflect.engine()
            plural_name = p.plural(resource.Meta.name.lower())
            url = '{}/{}'.format(base_url, plural_name)
        return cls._parse_url_and_validate(url)

    @classmethod
    def get_single_resource_url(cls, url, uid, **kwargs):
        """
        Construct the URL for talking to an individual resource.

        http://myapi.com/api/resource/1

        Args:
            url: The url for this resource
            uid: The unique identifier for an individual resource
            kwargs: Additional keyword argueents
        returns:
            final_url: The URL for this individual resource
        """

        if uid is None:
            raise MissingUidException
        url = '{}/{}'.format(url, uid)
        return cls._parse_url_and_validate(url)

    @staticmethod
    def get_method_name(resource, method_type):
        """
        Generate a method name for this resource based on the method type.
        """
        return '{}_{}'.format(method_type.lower(), resource.Meta.name.lower())

    @classmethod
    def _parse_url_and_validate(cls, url):
        """
        Recieves a URL string and validates it using urlparse.

        Args:
            url: A URL string
        Returns:
            parsed_url: A validated URL
        Raises:
            BadURLException
        """
        parsed_url = urlparse(url)
        if parsed_url.scheme and parsed_url.netloc:
            final_url = parsed_url.geturl()
        else:
            raise BadURLException
        return final_url


class HypermediaResource(BaseResource, HTTPClient):
    """
    A HypermediaResource is similar to a BaseResource except
    it understands relationships between attributes that
    are URLs to related registered resources.
    """
    class Meta(BaseResource.Meta):
        # HypermediaResource requires a base_url attribute
        base_url = NotImplemented
        related_resources = ()

    def __init__(self, *args, **kwargs):
        super(HypermediaResource, self).__init__(*args, **kwargs)
        self.session = requests.Session()

    def set_related_method(self, resource, value, base_url):
        """
        Using reflection, generate the related method and return it.
        """
        method_name = self.get_method_name(resource, 'get')

        url = resource.get_resource_url(
            resource, base_url=base_url
        )

        def get(self, method_type='GET', method_name=method_name,
                url=url, valid_status_codes=self.Meta.valid_status_codes,
                resource=resource, data=None, uid=None, **kwargs):
            return self.call_api(
                method_type, method_name,
                url, valid_status_codes, resource,
                data, uid=uid, **kwargs)

        setattr(
            self, method_name,
            types.MethodType(get, self)
        )

    def match_urls_to_resources(self, url_values):
        """
        For the list of related resources, and the list of
        valid URLs, try and match them up.

        If they match, assign a method to this class.

        Args:
            url_values: A dictionary of keys and URL strings that
                        could be related resources.
        Returns:
            valid_values: The values that are valid
        """
        valid_values = {}
        for resource in self.Meta.related_resources:
            for k, v in url_values.items():
                resource_url = resource.get_resource_url(
                    resource, resource.Meta.base_url)
                if resource_url in v:
                    self.set_related_method(
                        resource, v, resource.Meta.base_url)
                    valid_values[k] = v
        return valid_values

    def set_attributes(self, **kwargs):
        """
        Similar to BaseResource.set_attributes except
        it will attempt to match URL strings with registered
        related resources, and build their get_* method and
        attach it to this resource.
        """
        if not self.Meta.related_resources:
            super(HypermediaResource, self).set_attributes(**kwargs)

        # Extract all the values that are URLs
        url_values = {}
        for k, v in kwargs.items():
            try:
                self._parse_url_and_validate(v)
                url_values[k] = v
            except BadURLException:
                # This is a badly formed URL or not a URL at all, so skip
                pass
        # Assign the valid method values and then remove them from the kwargs
        assigned_values = self.match_urls_to_resources(url_values)
        [kwargs.pop(k, None) for k in assigned_values.keys()]
        # Assign the rest as attributes.
        for field, value in kwargs.items():
                if field in self.Meta.attributes:
                    setattr(self, field, value)
