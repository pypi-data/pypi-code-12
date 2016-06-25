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
        pagination_key = 'objects'

    @classmethod
    def get_single_resource_url(cls, url, uid, **kwargs):
        if kwargs.get('page'):
            return '{}?page={}'.format(
                url,
                kwargs.get('page')
            )
        if uid:
            return '{}/{}'.format(url, uid)
        else:
            return url


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


# Hypermedia fixtures

class HypermediaAuthorsResource(resources.HypermediaResource):

    class Meta(resources.HypermediaResource.Meta):
        name = 'Authors'
        resource_name = 'authors'
        base_url = 'http://dev/api'
        identifier = 'name'
        attributes = (
            'name',
            'slug',
            'another_thing',
        )
        methods = (
            'get',
        )


class HypermediaBlogsResource(resources.HypermediaResource):

    class Meta(resources.HypermediaResource.Meta):
        name = 'Blogs'
        identifier = 'name'
        base_url = 'http://dev/api'
        attributes = (
            'name',
            'slug',
            'another_thing',
            'author',
        )
        methods = (
            'get',
        )

        related_resources = (
            HypermediaAuthorsResource,
        )


class HypermediaBlogTestClient(clients.BaseClient):

    class Meta(clients.BaseClient.Meta):
        name = 'test_hyper_blog_client'
        base_url = 'http://dev/api'
        resources = (
            HypermediaBlogsResource,
            HypermediaAuthorsResource,
        )
