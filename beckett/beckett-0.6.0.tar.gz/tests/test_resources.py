#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_resources
----------------------------------

Tests for `beckett.resources` module.
"""

import responses

from beckett.resources import BaseResource

from tests.fixtures import (
    PeopleResource, HypermediaAuthorsResource, HypermediaBlogsResource
)


def test_base_resource_attributes():
    """
    Base class tests
    """

    model = BaseResource(id='1')
    assert model.__str__() == '<Resource | 1>'


def test_custom_resource():
    """
    Test our own custom resource - MyTestResource
    """
    data = {
        'name': 'Wort wort',
        'slug': 'sluggy',
        'not_valid': 'nooo'
    }
    instance = PeopleResource(**data)
    # We should have this attribute
    assert hasattr(instance, 'name')
    # But this one is missing
    assert not hasattr(instance, 'another_thing')
    # and this one is not valid
    assert not hasattr(instance, 'not_valid')
    assert instance.__str__() == '<People | Wort wort>'
    # It should also have parent Meta attributes
    assert hasattr(instance.Meta, 'valid_status_codes')


def test_hypermedia_custom_resource():
    """
    Test our custom Hypermedia resource loads correctly
    """
    data = {
        'name': 'Wort wort',
        'slug': 'sluggy',
        'not_valid': 'nooo',
        'author': 'http://dev/api/authors/1'
    }
    instance = HypermediaBlogsResource(**data)
    assert hasattr(instance, 'get_authors')


def test_hypermedia_custom_resource_non_registered_urls():
    """
    Test our custom Hypermedia resource handles
    URls that aren't registered.
    """
    data = {
        'name': 'Wort wort',
        'slug': 'sluggy',
        'not_valid': 'nooo',
        # This should not appear!
        'author': 'http://dev/api/foobar/1'
    }
    instance = HypermediaBlogsResource(**data)
    assert not hasattr(instance, 'get_authors')


@responses.activate
def test_hypermedia_custom_resource_calling():
    """
    Test our custom Hypermedia resource make HTTP calls correctly
    """
    responses.add(responses.GET, 'http://dev/api/authors/1',
                  body='''
                    {"id": "1", "title": "blog title",
                     "slug": "blog-title",
                     "content": "This is some content"}''',
                  status=200,
                  content_type='application/json')
    data = {
        'name': 'Wort wort',
        'slug': 'sluggy',
        'not_valid': 'nooo',
        'author': 'http://dev/api/authors/1'
    }
    instance = HypermediaBlogsResource(**data)
    response = instance.get_authors(uid=1)
    assert isinstance(response[0], HypermediaAuthorsResource)
