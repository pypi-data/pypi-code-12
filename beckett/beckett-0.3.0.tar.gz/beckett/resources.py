# -*- coding: utf-8 -*-

import inflect

from .constants import DEFAULT_VALID_STATUS_CODES
from .exceptions import MissingUidException


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
        # The key with which you uniquely identify this resource.
        identifier = 'id'
        # Acceptable attributes that you want to display in this resource.
        attributes = (identifier,)
        # HTTP status codes that are considered "acceptable"
        # when calling this resource
        acceptable_status_codes = DEFAULT_VALID_STATUS_CODES

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
        """
        for field, value in kwargs.items():
            if field in self.Meta.attributes:
                setattr(self, field, value)

    @staticmethod
    def get_resource_url(cls, base_url):
        """
        Construct the URL for talking to this resource.

        i.e.:

        http://myapi.com/api/resource

        Note that this is NOT the method for calling individual instances i.e.

        http://myapi.com/api/resource/1

        Subclass the `get_single_resource_url` method to modify that.

        Subclass this method to customise your resource URL structure.
        """
        p = inflect.engine()
        plural_name = p.plural(cls.Meta.name.lower())
        return '{}/{}'.format(base_url, plural_name)

    @staticmethod
    def get_single_resource_url(resource_url, uid):
        """
        Construct the URL for talking to an individual resource.

        http://myapi.com/api/resource/1
        """

        if uid is None:
            raise MissingUidException
        return '{}/{}'.format(resource_url, uid)
