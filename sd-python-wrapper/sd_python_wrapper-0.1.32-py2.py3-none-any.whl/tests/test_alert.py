#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from mock import patch
from serverdensity.wrapper import ApiClient
from serverdensity.wrapper import Alert
from tests.basetest import BaseTest


class AlertTest(BaseTest):

    @patch.object(ApiClient, '_make_request')
    def setUp(self, mock_make_request):
        self.alertobj = self.get_json('/json/alert.json')

        self.client = ApiClient('aeou')
        self.client._make_request = mock_make_request
        self.client._make_request.return_value = self.alertobj
        self.alert = Alert(api=self.client)

    def test_alert_create(self):
        data = {'data': 'alert'}
        self.alert.create(data)
        self.client._make_request.assert_called_with(
            data=data,
            method='POST',
            url=Alert.PATHS['create'],
            params=None
        )

    def test_alert_delete(self):
        self.alert.delete(1)
        self.client._make_request.assert_called_with(
            data=None,
            method='DELETE',
            url=Alert.PATHS['delete'].format(1),
            params=None
        )

    def test_alert_list(self):
        self.client._make_request.return_value = [self.alertobj]
        self.alert.list()
        self.client._make_request.assert_called_with(
            data=None,
            method='GET',
            url=Alert.PATHS['list'],
            params=None
        )

    def test_alert_update(self):
        data = {'name': 'test', 'type': 'alert'}
        self.alert.update(_id=1, data=data)
        self.client._make_request.assert_called_with(
            data=data,
            method='PUT',
            url=Alert.PATHS['update'].format(1),
            params=None
        )

    def test_alert_view(self):
        self.alert.view(1)
        self.client._make_request.assert_called_with(
            data=None,
            method='GET',
            url=Alert.PATHS['view'].format(1),
            params=None
        )

    def test_alert_triggered(self):
        self.client._make_request.return_value = [self.alertobj]
        self.alert.triggered(1, 'device', True)
        self.client._make_request.assert_called_with(
            data=None,
            method='GET',
            url=Alert.PATHS['triggered'],
            params={'filter': '{"config.subjectId": 1, "config.subjectType": "device", "fixed": true}'}
        )

    def test_alert_device_metrics(self):
        self.alert.device_metrics()
        self.client._make_request.assert_called_with(
            data=None,
            method='GET',
            url=Alert.PATHS['device_metrics'],
            params=None
        )

    def test_alert_service_metrics(self):
        self.alert.service_metrics()
        self.client._make_request.assert_called_with(
            data=None,
            method='GET',
            url=Alert.PATHS['service_metrics'],
            params=None
        )

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
