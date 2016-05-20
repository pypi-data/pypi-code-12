from __future__ import unicode_literals
from __future__ import print_function

import unittest

from mock import patch
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.policies.appsensor import UserAgentSensor

class UserAgentSensorTest(unittest.TestCase):

    def create_default_sensor_test(self):
        sensor = UserAgentSensor()
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.empty_enabled, False)

    def create_enabled_sensor_test(self):
        sensor = UserAgentSensor({"enabled": True})
        self.assertEqual(sensor.enabled, True)

    def create_empty_enabled_sensor_test(self):
        sensor = UserAgentSensor({"empty_enabled": True})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.empty_enabled, True)

    def with_disabled_sensor_check_test(self):
        sensor = UserAgentSensor({"enabled": False})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        with patch('tcell_agent.policies.appsensor.user_agent_sensor.sendEvent') as patched_send_event:
            sensor.check(meta)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_user_agent_is_present_check_test(self):
        sensor = UserAgentSensor({"enabled": True, "empty_enabled": True})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        meta.request_data(1024, {}, {}, {}, "", "user agent")
        with patch('tcell_agent.policies.appsensor.user_agent_sensor.sendEvent') as patched_send_event:
            sensor.check(meta)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_user_agent_is_none_check_test(self):
        sensor = UserAgentSensor({"enabled": True, "empty_enabled": True})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        meta.request_data(1024, {}, {}, {}, "", None)
        with patch('tcell_agent.policies.appsensor.user_agent_sensor.sendEvent') as patched_send_event:
            sensor.check(meta)
            patched_send_event.assert_called_once_with(meta, UserAgentSensor.DP_CODE, None, None)

    def with_enabled_sensor_and_user_agent_is_empty_string_check_test(self):
        sensor = UserAgentSensor({"enabled": True, "empty_enabled": True})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        meta.request_data(1024, {}, {}, {}, "", "")
        with patch('tcell_agent.policies.appsensor.user_agent_sensor.sendEvent') as patched_send_event:
            sensor.check(meta)
            patched_send_event.assert_called_once_with(meta, UserAgentSensor.DP_CODE, None, None)

    def with_enabled_sensor_and_user_agent_is_blank_string_check_test(self):
        sensor = UserAgentSensor({"enabled": True, "empty_enabled": True})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        meta.request_data(1024, {}, {}, {}, "", "   \t \n")
        with patch('tcell_agent.policies.appsensor.user_agent_sensor.sendEvent') as patched_send_event:
            sensor.check(meta)
            patched_send_event.assert_called_once_with(meta, UserAgentSensor.DP_CODE, None, None)
