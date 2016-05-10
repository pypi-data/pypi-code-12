from __future__ import unicode_literals
from __future__ import print_function

import unittest

from mock import patch
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.policies.appsensor import ResponseCodesSensor

class ResponseCodesSensorTest(unittest.TestCase):

    def create_default_sensor_test(self):
        sensor = ResponseCodesSensor()
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.series_400_enabled, False)
        self.assertEqual(sensor.series_500_enabled, False)

    def create_enabled_sensor_test(self):
        sensor = ResponseCodesSensor({"enabled": True})
        self.assertEqual(sensor.enabled, True)
        self.assertEqual(sensor.series_400_enabled, False)
        self.assertEqual(sensor.series_500_enabled, False)

    def create_sensor_with_series_400_enabled_test(self):
        sensor = ResponseCodesSensor({"series_400_enabled": True})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.series_400_enabled, True)
        self.assertEqual(sensor.series_500_enabled, False)

    def create_sensor_with_series_500_enabled_test(self):
        sensor = ResponseCodesSensor({"series_500_enabled": True})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.series_400_enabled, False)
        self.assertEqual(sensor.series_500_enabled, True)

    def with_disabled_sensor_check_test(self):
        sensor = ResponseCodesSensor({"enabled": False})
        with patch('tcell_agent.policies.appsensor.response_codes_sensor.sendEvent') as patched_send_event:
            sensor.check({}, 200)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_200_response_code_check_test(self):
        sensor = ResponseCodesSensor({"enabled": True, "series_400_enabled": True, "series_500_enabled": True})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        with patch('tcell_agent.policies.appsensor.response_codes_sensor.sendEvent') as patched_send_event:
            sensor.check(meta, 200)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_300_response_code_check_test(self):
        sensor = ResponseCodesSensor({"enabled": True, "series_400_enabled": True, "series_500_enabled": True})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        with patch('tcell_agent.policies.appsensor.response_codes_sensor.sendEvent') as patched_send_event:
            sensor.check(meta, 300)
            self.assertFalse(patched_send_event.called)

    def with_disabled_400_series_and_400_response_code_check_test(self):
        sensor = ResponseCodesSensor({"enabled": True, "series_400_enabled": False, "series_500_enabled": True})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        with patch('tcell_agent.policies.appsensor.response_codes_sensor.sendEvent') as patched_send_event:
            sensor.check(meta, 400)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_400_response_code_check_test(self):
        sensor = ResponseCodesSensor({"enabled": True, "series_400_enabled": True, "series_500_enabled": True})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        with patch('tcell_agent.policies.appsensor.response_codes_sensor.sendEvent') as patched_send_event:
            sensor.check(meta, 400)
            patched_send_event.assert_called_once_with(meta, ResponseCodesSensor.RESPONSE_CODE_DP_DICT[4], "400", None)

    def with_enabled_sensor_and_401_response_code_check_test(self):
        sensor = ResponseCodesSensor({"enabled": True, "series_400_enabled": True, "series_500_enabled": True})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        with patch('tcell_agent.policies.appsensor.response_codes_sensor.sendEvent') as patched_send_event:
            sensor.check(meta, 401)
            patched_send_event.assert_called_once_with(meta, ResponseCodesSensor.RESPONSE_CODE_DP_DICT[401], "401", None)

    def with_enabled_sensor_and_403_response_code_check_test(self):
        sensor = ResponseCodesSensor({"enabled": True, "series_400_enabled": True, "series_500_enabled": True})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        with patch('tcell_agent.policies.appsensor.response_codes_sensor.sendEvent') as patched_send_event:
            sensor.check(meta, 403)
            patched_send_event.assert_called_once_with(meta, ResponseCodesSensor.RESPONSE_CODE_DP_DICT[403], "403", None)

    def with_enabled_sensor_and_404_response_code_check_test(self):
        sensor = ResponseCodesSensor({"enabled": True, "series_400_enabled": True, "series_500_enabled": True})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        with patch('tcell_agent.policies.appsensor.response_codes_sensor.sendEvent') as patched_send_event:
            sensor.check(meta, 404)
            patched_send_event.assert_called_once_with(meta, ResponseCodesSensor.RESPONSE_CODE_DP_DICT[404], "404", None)

    def with_disabled_500_series_and_500_response_code_check_test(self):
        sensor = ResponseCodesSensor({"enabled": True, "series_400_enabled": True, "series_500_enabled": False})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        with patch('tcell_agent.policies.appsensor.response_codes_sensor.sendEvent') as patched_send_event:
            sensor.check(meta, 500)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_500_response_code_check_test(self):
        sensor = ResponseCodesSensor({"enabled": True, "series_400_enabled": True, "series_500_enabled": True})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        with patch('tcell_agent.policies.appsensor.response_codes_sensor.sendEvent') as patched_send_event:
            sensor.check(meta, 500)
            patched_send_event.assert_called_once_with(meta, ResponseCodesSensor.RESPONSE_CODE_DP_DICT[500], "500", None)

    def with_enabled_sensor_and_501_response_code_check_test(self):
        sensor = ResponseCodesSensor({"enabled": True, "series_400_enabled": True, "series_500_enabled": True})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        with patch('tcell_agent.policies.appsensor.response_codes_sensor.sendEvent') as patched_send_event:
            sensor.check(meta, 501)
            patched_send_event.assert_called_once_with(meta, ResponseCodesSensor.RESPONSE_CODE_DP_DICT[5], "501", None)
