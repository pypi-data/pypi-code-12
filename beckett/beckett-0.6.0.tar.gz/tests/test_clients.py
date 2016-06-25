#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_clients
----------------------------------

Tests for `beckett.clients` module.
"""

import json

from beckett.exceptions import InvalidStatusCodeError

import pytest

import responses

from .fixtures import BlogResource, BlogTestClient, PlainTestClient


@responses.activate
def test_custom_client():
    """
    Test our own custom client - PlainTestClient
    """
    client = PlainTestClient()
    # Our PlainTestClient should have a registered GET method
    # For the Testy resource
    assert hasattr(client, 'get_people')
    responses.add(responses.GET, 'http://dev/api/peoples/1',
                  body='''
                    {"id": 1, "title": "blog title",
                     "slug": "blog-title",
                     "content": "This is some content"}''',
                  status=200,
                  content_type='application/json')
    people_resource = client.get_people(uid=1)
    assert people_resource[0].slug == 'blog-title'


@responses.activate
def test_custom_client_get_methods():
    """
    Make HTTP GET calls against mocking and inspect their responses.
    """

    client = BlogTestClient()
    # Add a mocked response for a single resource
    responses.add(responses.GET, 'http://dev/api/blogs/1',
                  body='''
                    {"id": 1, "title": "blog title",
                     "slug": "blog-title",
                     "content": "This is some content"}''',
                  status=200,
                  content_type='application/json')
    result = client.get_blog(uid=1)
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == 'http://dev/api/blogs/1'
    assert responses.calls[0].request.method == 'GET'
    assert isinstance(result, list)
    assert isinstance(result[0], BlogResource)
    resource = result[0]
    assert resource.title == 'blog title'


@responses.activate
def test_custom_client_post_methods():
    """
    Make HTTP POST calls against mocking and inspect the response.
    """
    client = BlogTestClient()
    responses.add(responses.POST, 'http://dev/api/blogs',
                  body='''
                    {"id": 1, "title": "blog title",
                     "slug": "blog-title",
                     "content": "This is some content"}''',
                  status=201,
                  content_type='application/json')
    data = {
        "title": "blog title",
        "slug": "blog-title",
        "content": "This is some content"
    }
    result = client.post_blog(data=data)
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == 'http://dev/api/blogs'
    assert responses.calls[0].request.body == json.dumps(data)
    assert responses.calls[0].request.method == 'POST'
    assert isinstance(result, list)
    assert isinstance(result[0], BlogResource)
    resource = result[0]
    assert resource.title == 'blog title'


@responses.activate
def test_custom_client_delete_methods():
    """
    Make HTTP DELETE calls against mocking and inspect the response.
    """
    client = BlogTestClient()
    responses.add(responses.DELETE, 'http://dev/api/blogs/1',
                  body='',
                  status=204,
                  content_type='application/json')
    result = client.delete_blog(uid=1)
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == 'http://dev/api/blogs/1'
    assert responses.calls[0].request.method == 'DELETE'


@responses.activate
def test_custom_client_put_methods():
    """
    Make HTTP PUT calls against mocking and inspect the response.
    """
    client = BlogTestClient()
    responses.add(responses.PUT, 'http://dev/api/blogs/1',
                  body='''
                    {"id": 1, "title": "blog title",
                     "slug": "blog-title",
                     "content": "This is some content"}''',
                  status=200,
                  content_type='application/json')
    data = {
        "title": "blog title",
        "slug": "blog-title",
        "content": "This is some content"
    }
    result = client.put_blog(uid=1, data=data)
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == 'http://dev/api/blogs/1'
    assert responses.calls[0].request.body == json.dumps(data)
    assert responses.calls[0].request.method == 'PUT'
    assert isinstance(result, list)
    assert isinstance(result[0], BlogResource)
    resource = result[0]
    assert resource.title == 'blog title'


@responses.activate
def test_custom_client_patch_methods():
    """
    Make HTTP PATCH calls against mocking and inspect the response.
    """
    client = BlogTestClient()
    responses.add(responses.PATCH, 'http://dev/api/blogs/1',
                  body='''
                    {"id": 1, "title": "blog title",
                     "slug": "blog-title",
                     "content": "This is some content"}''',
                  status=200,
                  content_type='application/json')
    data = {
        "title": "blog title",
    }
    result = client.patch_blog(uid=1, data=data)
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == 'http://dev/api/blogs/1'
    assert responses.calls[0].request.body == json.dumps(data)
    assert responses.calls[0].request.method == 'PATCH'
    assert isinstance(result, list)
    assert isinstance(result[0], BlogResource)
    resource = result[0]
    assert resource.title == 'blog title'


@responses.activate
def test_custom_client_bad_status_codes():
    """
    Make HTTP calls and mock back bad responses to make sure errors are raised.
    """
    client = BlogTestClient()
    # HTTP 404 error!
    responses.add(responses.GET, 'http://dev/api/blogs/1',
                  body='''
                    {"id": 1, "title": "blog title",
                     "slug": "blog-title",
                     "content": "This is some content"}''',
                  status=404,
                  content_type='application/json')
    with pytest.raises(InvalidStatusCodeError):
        client.get_blog(uid=1)
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == 'http://dev/api/blogs/1'
    assert responses.calls[0].request.method == 'GET'


@responses.activate
def test_custom_client_get_many_resource_methods():
    """
    Make HTTP GET calls that receive many resources renders more a list of
    resource instances.
    """

    client = BlogTestClient()
    # Add a mocked response for a single resource
    responses.add(responses.GET, 'http://dev/api/blogs',
                  body='''[
                    {"id": 1, "title": "blog title",
                     "slug": "blog-title",
                     "content": "This is some content"},
                     {"id": 1, "title": "blog title",
                      "slug": "blog-title",
                      "content": "This is some content"}]''',
                  status=200,
                  content_type='application/json')

    result = client.get_blog()
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == 'http://dev/api/blogs'
    assert responses.calls[0].request.method == 'GET'
    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], BlogResource)
    resource1 = result[0]
    assert resource1.title == 'blog title'


@responses.activate
def test_custom_client_get_paginated_response_methods():
    """
    Make HTTP GET calls using pagination
    """

    client = BlogTestClient()
    # Add a mocked response
    responses.add(responses.GET, 'http://dev/api/blogs',
                  body='''{
                    "count": 2,
                    "next": "http://dev/api/blogs?page=2",
                    "objects": [
                        {
                            "title": "blog title"
                        },
                        {
                            "title": "Second title"
                        }
                        ]
                    }''',
                  status=200,
                  content_type='application/json')

    result = client.get_blog(page=1)
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == 'http://dev/api/blogs?page=1'
    assert responses.calls[0].request.method == 'GET'
    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], BlogResource)
    resource = result[0]
    assert resource.title == 'blog title'
    resource2 = result[1]
    assert resource2.title == 'Second title'
