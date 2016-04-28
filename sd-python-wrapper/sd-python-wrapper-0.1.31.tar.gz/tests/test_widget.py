#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from mock import patch
from tests.basetest import BaseTest
from serverdensity.wrapper import ApiClient
from serverdensity.wrapper import Widget


class WidgetTest(BaseTest):

    @patch.object(ApiClient, '_make_request')
    def setUp(self, mock_make_request):
        self.widgetobj = self.get_json('/json/widget.json')

        self.client = ApiClient('aeou')
        self.client._make_request = mock_make_request
        self.client._make_request.return_value = self.widgetobj
        self.widget = Widget(api=self.client)

    def test_widgetobject_with_data(self):
        widget = Widget(self.client, self.widgetobj)
        self.assertEqual(self.widgetobj['_id'], widget._id)

    def test_widget_create(self):
        data = {'data': 'widget'}
        self.widget.create(data)
        self.client._make_request.assert_called_with(
            data=data,
            method='POST',
            url=Widget.PATHS['create'],
            params=None
        )

    def test_widget_duplicate(self):
        self.widget.duplicate(1)
        self.client._make_request.assert_called_with(
            data=None,
            method='POST',
            url=Widget.PATHS['duplicate'].format(1),
            params=None
        )

    def test_widget_delete(self):
        self.widget.delete(1)
        self.client._make_request.assert_called_with(
            data=None,
            method='DELETE',
            url=Widget.PATHS['delete'].format(1),
            params=None
        )

    def test_widget_list(self):
        self.client._make_request.return_value = [self.widgetobj]
        self.widget.list()
        self.client._make_request.assert_called_with(
            data=None,
            method='GET',
            url=Widget.PATHS['list'],
            params=None
        )

    def test_widget_update(self):
        data = {'name': 'test', 'type': 'widget'}
        self.widget.update(_id=1, data=data)
        self.client._make_request.assert_called_with(
            data=data,
            method='PUT',
            url=Widget.PATHS['update'].format(1),
            params=None
        )

    def test_widget_view(self):
        self.widget.view(1)
        self.client._make_request.assert_called_with(
            data=None,
            method='GET',
            url=Widget.PATHS['view'].format(1),
            params=None
        )


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
