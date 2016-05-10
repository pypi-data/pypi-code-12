from __future__ import unicode_literals
from __future__ import print_function

import unittest

from mock import patch
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.policies.appsensor import RequestSizeSensor

class RequestSizeSensorTest(unittest.TestCase):

    def create_default_sensor_test(self):
        sensor = RequestSizeSensor()
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.limit, 524288)
        self.assertEqual(sensor.exclude_routes, {})

    def create_enabled_sensor_test(self):
        sensor = RequestSizeSensor({"enabled": True})
        self.assertEqual(sensor.enabled, True)
        self.assertEqual(sensor.limit, 524288)
        self.assertEqual(sensor.exclude_routes, {})

    def create_sensor_with_limit_test(self):
        sensor = RequestSizeSensor({"limit": 1024})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.limit, 1024)
        self.assertEqual(sensor.exclude_routes, {})

    def create_sensor_with_exclude_routes_test(self):
        sensor = RequestSizeSensor({"exclude_routes": ["1", "10", "20"]})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.limit, 524288)
        self.assertEqual(sensor.exclude_routes, {"1": True, "10": True, "20": True})

    def with_disabled_sensor_check_test(self):
        sensor = RequestSizeSensor({"enabled": False})
        sensor.check({}, 10)

    def with_enabled_sensor_and_size_is_too_big_but_route_id_is_excluded_check_test(self):
        sensor = RequestSizeSensor({"enabled": True, "limit": 1024, "exclude_routes": ["23947"]})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        with patch('tcell_agent.policies.appsensor.size_sensor.sendEvent') as patched_send_event:
            sensor.check(meta, 2048)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_size_is_ok_check_test(self):
        sensor = RequestSizeSensor({"enabled": True, "limit": 1024})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "route_id",
            session_id="session_id",
            user_id="user_id"
        )
        with patch('tcell_agent.policies.appsensor.size_sensor.sendEvent') as patched_send_event:
            sensor.check(meta, 10)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_size_is_too_big_check_test(self):
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "route_id",
            session_id="session_id",
            user_id="user_id"
        )

        sensor = RequestSizeSensor({"enabled": True, "limit": 1024})

        with patch('tcell_agent.policies.appsensor.size_sensor.sendEvent') as patched_send_event:
            sensor.check(meta, 3072)
            patched_send_event.assert_called_once_with(meta, RequestSizeSensor.DP_UNUSUAL_REQUEST_SIZE, '3072', None)
