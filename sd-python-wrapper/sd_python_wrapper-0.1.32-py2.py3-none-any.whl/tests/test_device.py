#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import json

from mock import patch
from serverdensity.wrapper import ApiClient
from serverdensity.wrapper import Device
from tests.basetest import BaseTest

class DeviceTest(BaseTest):

    @patch.object(ApiClient, '_make_request')
    def setUp(self, mock_make_request):
        self.deviceobj = self.get_json('/json/device.json')

        self.client = ApiClient('aeou')
        self.client._make_request = mock_make_request
        self.client._make_request.return_value = self.deviceobj
        self.device = Device(api=self.client)

    def test_device_create(self):
        data = {'data': 'device'}
        self.device.create(data)
        self.client._make_request.assert_called_with(
            data=data,
            method='POST',
            url=Device.PATHS['create'],
            params=None
        )

    def test_device_delete(self):
        self.device.delete(1)
        self.client._make_request.assert_called_with(
            data=None,
            method='DELETE',
            url=Device.PATHS['delete'].format(1),
            params=None
        )

    def test_device_list(self):
        self.client._make_request.return_value = [self.deviceobj]
        self.device.list()
        self.client._make_request.assert_called_with(
            data=None,
            method='GET',
            url=Device.PATHS['list'],
            params=None
        )

    def test_device_search(self):
        self.client._make_request.return_value = [self.deviceobj]
        filter_data = {'name': 'test', 'type': 'device'}
        self.device.search(filtering=filter_data)
        self.client._make_request.assert_called_with(
            data=None,
            method='GET',
            url=Device.PATHS['search'],
            params={'filter': json.dumps(filter_data)}
        )

    def test_device_update(self):
        data = {'name': 'test', 'type': 'device'}
        self.device.update(_id=1, data=data)
        self.client._make_request.assert_called_with(
            data=data,
            method='PUT',
            url=Device.PATHS['update'].format(1),
            params=None
        )

    def test_device_view_by_agent(self):
        self.device.view_by_agent(1)
        self.client._make_request.assert_called_with(
            data=None,
            method='GET',
            url=Device.PATHS['view_by_agent'].format(1),
            params=None
        )

    def test_device_view(self):
        self.device.view(1)
        self.client._make_request.assert_called_with(
            data=None,
            method='GET',
            url=Device.PATHS['view'].format(1),
            params=None
        )

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
