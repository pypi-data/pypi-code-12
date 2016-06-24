from __future__ import unicode_literals
from __future__ import print_function

import unittest

from mock import patch
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.policies.appsensor import SqliSensor

class SqliSensorTest(unittest.TestCase):

    def create_default_sensor_test(self):
        sensor = SqliSensor()
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "sqli")
        self.assertEqual(sensor.libinjection, False)
        self.assertEqual(sensor.active_pattern_ids, {})
        self.assertEqual(sensor.exclusions, {})

    def create_enabled_sensor_test(self):
        sensor = SqliSensor({"enabled": True})
        self.assertEqual(sensor.enabled, True)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "sqli")
        self.assertEqual(sensor.libinjection, False)
        self.assertEqual(sensor.active_pattern_ids, {})
        self.assertEqual(sensor.exclusions, {})

    def create_excluded_headers_sensor_test(self):
        sensor = SqliSensor({"exclude_headers": True})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, True)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "sqli")
        self.assertEqual(sensor.libinjection, False)
        self.assertEqual(sensor.active_pattern_ids, {})
        self.assertEqual(sensor.exclusions, {})

    def create_excluded_forms_sensor_test(self):
        sensor = SqliSensor({"exclude_forms": True})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, True)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "sqli")
        self.assertEqual(sensor.libinjection, False)
        self.assertEqual(sensor.active_pattern_ids, {})
        self.assertEqual(sensor.exclusions, {})

    def create_excluded_cookies_sensor_test(self):
        sensor = SqliSensor({"exclude_cookies": True})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, True)
        self.assertEqual(sensor.dp, "sqli")
        self.assertEqual(sensor.libinjection, False)
        self.assertEqual(sensor.active_pattern_ids, {})
        self.assertEqual(sensor.exclusions, {})

    def create_libinjection_sensor_test(self):
        sensor = SqliSensor({"libinjection": True})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "sqli")
        self.assertEqual(sensor.libinjection, True)
        self.assertEqual(sensor.active_pattern_ids, {})
        self.assertEqual(sensor.exclusions, {})

    def create_active_pattern_ids_sensor_test(self):
        sensor = SqliSensor({"patterns": ["1", "2", "3"]})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "sqli")
        self.assertEqual(sensor.libinjection, False)
        self.assertEqual(sensor.active_pattern_ids, {"1": True, "2": True, "3": True})
        self.assertEqual(sensor.exclusions, {})

    def create_exclusions_sensor_test(self):
        sensor = SqliSensor({"exclusions": {"word": ["form", "header"]}})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "sqli")
        self.assertEqual(sensor.libinjection, False)
        self.assertEqual(sensor.active_pattern_ids, {})
        self.assertEqual(sensor.exclusions, {"word": ["form", "header"]})

    def with_disabled_sensor_check_test(self):
        sensor = SqliSensor({"enabled": False})

        with patch('tcell_agent.policies.appsensor.injection_sensor.sendEvent') as patched_send_event:
            sensor.check("get", {}, None, None)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_no_vuln_params_check_test(self):
        sensor = SqliSensor({"enabled": True})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )

        with patch('tcell_agent.policies.appsensor.injection_sensor.sendEvent') as patched_send_event:
            sensor.check("get", meta, None, None)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_vuln_params_check_test(self):
        sensor = SqliSensor({"enabled": True, "patterns": ["1"]})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )

        with patch('tcell_agent.policies.appsensor.injection_sensor.sendEvent') as patched_send_event:
            is_sqli = sensor.check("get", meta, "dirty", "Erwin' OR '1'='1")
            self.assertTrue(is_sqli)
            patched_send_event.assert_called_once_with(meta, "sqli",  'dirty', '{"t": "get"}', None, "1")
