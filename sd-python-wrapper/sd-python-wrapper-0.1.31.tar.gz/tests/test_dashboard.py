#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from mock import patch
from serverdensity.wrapper import ApiClient
from serverdensity.wrapper import Dashboard
from tests.basetest import BaseTest

class DashboardTest(BaseTest):

    @patch.object(ApiClient, '_make_request')
    def setUp(self, mock_make_request):
        self.dashobj = self.get_json('/json/dashboard.json')

        self.client = ApiClient('aeou')
        self.client._make_request = mock_make_request
        self.client._make_request.return_value = self.dashobj
        self.dashboard = Dashboard(api=self.client)

    def test_dashboard_create(self):
        data = {'data': 'dashboard'}
        self.dashboard.create(data)
        self.client._make_request.assert_called_with(
            data=data,
            method='POST',
            url=Dashboard.PATHS['create'],
            params=None
        )

    def test_dashboard_delete(self):
        self.dashboard.delete(1)
        self.client._make_request.assert_called_with(
            data=None,
            method='DELETE',
            url=Dashboard.PATHS['delete'].format(1),
            params=None
        )

    def test_dashboard_list(self):
        self.client._make_request.return_value = [self.dashobj]
        self.dashboard.list()
        self.client._make_request.assert_called_with(
            data=None,
            method='GET',
            url=Dashboard.PATHS['list'],
            params=None
        )

    def test_dashboard_update(self):
        data = {'name': 'test', 'type': 'dashboard'}
        self.dashboard.update(_id=1, data=data)
        self.client._make_request.assert_called_with(
            data=data,
            method='PUT',
            url=Dashboard.PATHS['update'].format(1),
            params=None
        )

    def test_dashboard_view(self):
        self.dashboard.view(1)
        self.client._make_request.assert_called_with(
            data=None,
            method='GET',
            url=Dashboard.PATHS['view'].format(1),
            params=None
        )

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
