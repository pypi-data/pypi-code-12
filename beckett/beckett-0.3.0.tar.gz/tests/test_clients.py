#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_clients
----------------------------------

Tests for `beckett.clients` module.
"""

import responses

from .fixtures import BlogResource, BlogTestClient, PlainTestClient


def test_custom_client():
    """
    Test our own custom client - PlainTestClient
    """
    client = PlainTestClient()
    # Our PlainTestClient should have a registered GET method
    # For the Testy resource
    assert hasattr(client, 'get_people')


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
    assert isinstance(result, list)
    assert isinstance(result[0], BlogResource)
    resource = result[0]
    assert resource.title == 'blog title'
