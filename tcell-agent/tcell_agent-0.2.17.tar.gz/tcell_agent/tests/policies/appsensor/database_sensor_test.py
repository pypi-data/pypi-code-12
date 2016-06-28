from __future__ import unicode_literals
from __future__ import print_function

import unittest

from mock import patch
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.policies.appsensor import DatabaseSensor

class DatabaseSensorTest(unittest.TestCase):

    def create_default_sensor_test(self):
        sensor = DatabaseSensor()
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.max_rows, 1001)
        self.assertEqual(sensor.excluded_route_ids, {})

    def create_enabled_sensor_test(self):
        sensor = DatabaseSensor({"enabled": True})
        self.assertEqual(sensor.enabled, True)
        self.assertEqual(sensor.max_rows, 1001)
        self.assertEqual(sensor.excluded_route_ids, {})

    def create_sensor_with_max_rows_test(self):
        sensor = DatabaseSensor({"large_result": {"limit": 1024}})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.max_rows, 1024)
        self.assertEqual(sensor.excluded_route_ids, {})

    def create_sensor_with_exclude_routes_test(self):
        sensor = DatabaseSensor({"exclude_routes": ["1", "10", "20"]})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.max_rows, 1001)
        self.assertEqual(sensor.excluded_route_ids, {"1": True, "10": True, "20": True})

    def with_disabled_sensor_check_test(self):
        sensor = DatabaseSensor({"enabled": False, "large_result": {"limit": 1024}})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "route_id",
            session_id="session_id",
            user_id="user_id"
        )

        with patch('tcell_agent.policies.appsensor.database_sensor.sendEvent') as patched_send_event:
            sensor.check(meta, 3072)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_number_of_records_is_too_big_but_route_id_is_excluded_check_test(self):
        sensor = DatabaseSensor({"enabled": True, "large_result": {"limit": 1024}, "exclude_routes": ["23947"]})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        with patch('tcell_agent.policies.appsensor.database_sensor.sendEvent') as patched_send_event:
            sensor.check(meta, 2048)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_number_of_records_is_ok_check_test(self):
        sensor = DatabaseSensor({"enabled": True, "large_result": {"limit": 1024}})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "route_id",
            session_id="session_id",
            user_id="user_id"
        )
        with patch('tcell_agent.policies.appsensor.database_sensor.sendEvent') as patched_send_event:
            sensor.check(meta, 10)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_number_of_records_is_too_big_check_test(self):
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "route_id",
            session_id="session_id",
            user_id="user_id"
        )

        sensor = DatabaseSensor({"enabled": True, "large_result": {"limit": 1024}})

        with patch('tcell_agent.policies.appsensor.database_sensor.sendEvent') as patched_send_event:
            sensor.check(meta, 3072)
            patched_send_event.assert_called_once_with(meta, DatabaseSensor.DP_CODE, None, '{"rows": 3072}')
