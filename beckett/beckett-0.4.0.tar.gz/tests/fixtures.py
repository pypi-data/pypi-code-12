# -*- coding: utf-8 -*-

from beckett import clients, resources


class PeopleResource(resources.BaseResource):

    class Meta(resources.BaseResource.Meta):
        name = 'People'
        identifier = 'name'
        attributes = (
            'name',
            'slug',
            'another_thing',
        )
        methods = (
            'get',
        )


class BlogResource(resources.BaseResource):

    class Meta(resources.BaseResource.Meta):
        name = 'Blog'
        identifier = 'id'
        attributes = (
            'id',
            'title',
            'slug',
            'content',
        )
        methods = (
            'get',
            'post',
            'put',
            'patch',
            'delete',
        )


class PlainTestClient(clients.BaseClient):

    class Meta(clients.BaseClient.Meta):
        name = 'test_client'
        base_url = 'http://dev/api'
        resources = (
            PeopleResource,
        )


class BlogTestClient(clients.BaseClient):

    class Meta(clients.BaseClient.Meta):
        name = 'test_blog_client'
        base_url = 'http://dev/api'
        resources = (
            BlogResource,
        )
