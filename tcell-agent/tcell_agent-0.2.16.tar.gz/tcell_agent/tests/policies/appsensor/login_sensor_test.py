from __future__ import unicode_literals
from __future__ import print_function

import unittest

from mock import patch
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.policies.appsensor import LoginSensor
from tcell_agent.sanitize import SanitizeUtils

class LoginSensorTest(unittest.TestCase):

    def create_default_sensor_test(self):
        sensor = LoginSensor()
        self.assertEqual(sensor.enabled, False)

    def create_enabled_sensor_test(self):
        sensor = LoginSensor({"enabled": True})
        self.assertEqual(sensor.enabled, True)



    def with_disabled_sensor_check_test(self):
        sensor = LoginSensor({"enabled": False})

        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "route_id",
            session_id="session_id",
            user_id="user_id"
        )

        with patch('tcell_agent.policies.appsensor.login_sensor.sendEvent') as patched_send_event:
            sensor.check(meta, 'username')
            self.assertFalse(patched_send_event.called)

    def with_no_username_sensor_check_test(self):
        sensor = LoginSensor({"enabled": True})

        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "route_id",
            session_id="session_id",
            user_id="user_id"
        )

        with patch('tcell_agent.policies.appsensor.login_sensor.sendEvent') as patched_send_event:
            sensor.check(meta, None)
            patched_send_event.assert_called_once_with(meta, LoginSensor.LOGIN_FAILURE_DP, None, payload=None)

    def with_username_sensor_check_test(self):
        sensor = LoginSensor({"enabled": True})

        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "route_id",
            session_id="session_id",
            user_id="user_id"
        )

        with patch('tcell_agent.policies.appsensor.login_sensor.sendEvent') as patched_send_event:
            sensor.check(meta, "username")
            patched_send_event.assert_called_once_with(
                meta,
                LoginSensor.LOGIN_FAILURE_DP,
                SanitizeUtils.hmac("username"),
                payload=None
            )
