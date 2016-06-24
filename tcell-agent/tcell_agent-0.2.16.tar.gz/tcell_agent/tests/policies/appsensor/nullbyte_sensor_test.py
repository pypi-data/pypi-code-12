from __future__ import unicode_literals
from __future__ import print_function

import unittest

from mock import patch
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.appsensor.rules import AppSensorRuleManager
from tcell_agent.policies.appsensor import NullbyteSensor

class NullbyteSensorTest(unittest.TestCase):

    def create_default_sensor_test(self):
        sensor = NullbyteSensor()
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "null")
        self.assertEqual(sensor.active_pattern_ids, {})
        self.assertEqual(sensor.exclusions, {})

    def with_disabled_sensor_check_test(self):
        sensor = NullbyteSensor({"enabled": False})

        with patch('tcell_agent.policies.appsensor.injection_sensor.sendEvent') as patched_send_event:
            sensor.check("get", {}, None, None)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_no_vuln_params_check_test(self):
        sensor = NullbyteSensor({"enabled": True})
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
        sensor = NullbyteSensor({"enabled": True, "patterns": ["1"]})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )

        with patch('tcell_agent.policies.appsensor.injection_sensor.sendEvent') as patched_send_event:
            is_nullbyte = sensor.check("get", meta, "dirty", "\0blah\0\0\0")
            self.assertTrue(is_nullbyte)
            patched_send_event.assert_called_once_with(meta, "null",  'dirty', '{"t": "get"}', None, "1")

    def override_get_ruleset_test(self):
        with patch.object(AppSensorRuleManager, 'get_ruleset_for', return_value=None) as patched_get_ruleset_for:
            sensor = NullbyteSensor()
            sensor.get_ruleset()
            patched_get_ruleset_for.assert_called_once_with('nullbyte')
