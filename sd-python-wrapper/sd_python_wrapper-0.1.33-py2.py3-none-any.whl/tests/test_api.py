#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from mock import PropertyMock
from mock import MagicMock
from requests import Response
from requests import Session
import requests

from serverdensity.wrapper import ApiClient
from serverdensity.wrapper import Alert
from serverdensity.wrapper import Device
from serverdensity.wrapper import Dashboard
from serverdensity.wrapper import Metrics
from serverdensity.wrapper import Postback
from serverdensity.wrapper import Service
from serverdensity.wrapper import ServiceStatus
from serverdensity.wrapper import Tag
from serverdensity.wrapper import User

from serverdensity.wrapper.exceptions import HttpError
from serverdensity.wrapper.exceptions import TimeoutError
from serverdensity.wrapper.exceptions import ClientError


class ApiTest(unittest.TestCase):

    def setUp(self):
        self.data = {
            'property': 'result',
            'data': {'some_more': 'result'}
        }
        self.mock_response = MagicMock(autospec=Response)
        type(self.mock_response).status_code = PropertyMock(return_value=200)
        self.mock_response.raise_for_status.side_effect = requests.HTTPError()

        self.client = ApiClient('aoeu')
        self.client._session = MagicMock(spec_set=Session)
        self.client._session.send.return_value = self.mock_response

    def tearDown(self):
        pass

    def test_raises_httperror(self):
        type(self.mock_response).status_code = PropertyMock(return_value=400)
        with self.assertRaises(HttpError):
            self.client._make_request('GET', '/test')
        self.assertEqual(1, len(self.mock_response.reason.mock_calls))

    def test_raises_timeouterror(self):
        self.client._session.send.side_effect = requests.Timeout()
        with self.assertRaises(TimeoutError):
            self.client._make_request('GET', '/test')

    def test_raises_connectionerror(self):
        self.client._session.send.side_effect = requests.ConnectionError()
        with self.assertRaises(ClientError):
            self.client._make_request('GET', '/test')

    def test_response_returns_json(self):
        self.client._make_request('GET', '/test')
        self.assertEqual(self.mock_response.json.call_count, 1)

    def test_devices_property(self):
        isinstance(self.client.devices, Device)

    def test_services_property(self):
        isinstance(self.client.services, Service)

    def test_alerts_property(self):
        isinstance(self.client.alerts, Alert)

    def test_service_status_property(self):
        isinstance(self.client.service_status, ServiceStatus)

    def test_users_property(self):
        isinstance(self.client.users, User)

    def test_dashboards_property(self):
        isinstance(self.client.dashboards, Dashboard)

    def test_postbacks_property(self):
        isinstance(self.client.postbacks, Postback)

    def test_tag_property(self):
        isinstance(self.client.tags, Tag)

    def test_metrics_property(self):
        isinstance(self.client.metrics, Metrics)


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
