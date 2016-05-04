#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from mock import patch
from tests.basetest import BaseTest

from serverdensity.wrapper import ApiClient
from serverdensity.wrapper import Service


class ServiceTest(BaseTest):

    @patch.object(ApiClient, '_make_request')
    def setUp(self, mock_make_request):
        self.serviceobj = self.get_json('/json/service.json')

        self.client = ApiClient('aeou')
        self.client._make_request = mock_make_request
        self.client._make_request.return_value = self.serviceobj
        self.service = Service(api=self.client)

    def test_service_create(self):
        data = {'data': 'service'}
        self.service.create(data)
        self.client._make_request.assert_called_with(
            data=data,
            method='POST',
            url=Service.PATHS['create'],
            params=None
        )

    def test_service_delete(self):
        self.service.delete(1)
        self.client._make_request.assert_called_with(
            data=None,
            method='DELETE',
            url=Service.PATHS['delete'].format(1),
            params=None
        )

    def test_service_list(self):
        self.client._make_request.return_value = [self.serviceobj]
        self.service.list()
        self.client._make_request.assert_called_with(
            data=None,
            method='GET',
            url=Service.PATHS['list'],
            params=None
        )

    def test_service_search(self):
        self.client._make_request.return_value = [self.serviceobj]
        filter_data = {'name': 'test', 'type': 'service'}
        self.service.search(filtering=filter_data)
        self.client._make_request.assert_called_with(
            data=None,
            method='GET',
            url=Service.PATHS['search'],
            params={'filter': filter_data}
        )

    def test_service_update(self):
        data = {'name': 'test', 'type': 'service'}
        self.service.update(_id=1, data=data)
        self.client._make_request.assert_called_with(
            data=data,
            method='PUT',
            url=Service.PATHS['update'].format(1),
            params=None
        )

    def test_service_view(self):
        self.service.view(1)
        self.client._make_request.assert_called_with(
            data=None,
            method='GET',
            url=Service.PATHS['view'].format(1),
            params=None
        )

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
