#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from mock import patch
from tests.basetest import BaseTest
from serverdensity.wrapper import ApiClient
from serverdensity.wrapper import Tag


class TagTest(BaseTest):

    @patch.object(ApiClient, '_make_request')
    def setUp(self, mock_make_request):
        self.tagobj = self.get_json('/json/tag.json')

        self.client = ApiClient('aeou')
        self.client._make_request = mock_make_request
        self.client._make_request.return_value = self.tagobj
        self.tag = Tag(api=self.client)

    def test_tagobject_with_data(self):
        tag = Tag(self.client, self.tagobj)
        self.assertEqual(self.tagobj['_id'], tag._id)

    def test_tag_create(self):
        data = {'data': 'tag'}
        self.tag.create(data)
        self.client._make_request.assert_called_with(
            data=data,
            method='POST',
            url=Tag.PATHS['create'],
            params=None
        )

    def test_tag_delete(self):
        self.tag.delete(1)
        self.client._make_request.assert_called_with(
            data=None,
            method='DELETE',
            url=Tag.PATHS['delete'].format(1),
            params=None
        )

    def test_tag_list(self):
        self.client._make_request.return_value = [self.tagobj]
        self.tag.list()
        self.client._make_request.assert_called_with(
            data=None,
            method='GET',
            url=Tag.PATHS['list'],
            params=None
        )

    def test_tag_update(self):
        data = {'name': 'test', 'type': 'tag'}
        self.tag.update(_id=1, data=data)
        self.client._make_request.assert_called_with(
            data=data,
            method='PUT',
            url=Tag.PATHS['update'].format(1),
            params=None
        )

    def test_tag_view(self):
        self.tag.view(1)
        self.client._make_request.assert_called_with(
            data=None,
            method='GET',
            url=Tag.PATHS['view'].format(1),
            params=None
        )


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
