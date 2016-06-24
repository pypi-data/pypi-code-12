from __future__ import unicode_literals
from __future__ import print_function

import unittest

from mock import patch
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.policies.appsensor import RetrSensor

class RetrSensorTest(unittest.TestCase):

    def create_default_sensor_test(self):
        sensor = RetrSensor()
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "retr")
        self.assertEqual(sensor.active_pattern_ids, {})
        self.assertEqual(sensor.exclusions, {})

    def with_disabled_sensor_check_test(self):
        sensor = RetrSensor({"enabled": False})

        with patch('tcell_agent.policies.appsensor.injection_sensor.sendEvent') as patched_send_event:
            sensor.check("get", {}, None, None)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_no_vuln_params_check_test(self):
        sensor = RetrSensor({"enabled": True})
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
        sensor = RetrSensor({"enabled": True, "patterns": ["1"]})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )

        with patch('tcell_agent.policies.appsensor.injection_sensor.sendEvent') as patched_send_event:
            is_retr = sensor.check("get", meta, "dirty", "\nblah\r\n\n")
            self.assertTrue(is_retr)
            patched_send_event.assert_called_once_with(meta, "retr",  'dirty', '{"t": "get"}', None, "1")
