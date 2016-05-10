from __future__ import unicode_literals
from __future__ import print_function

import json
import unittest

from mock import patch
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.policies.appsensor import InjectionSensor
from tcell_agent.policies.appsensor import LoginSensor
from tcell_agent.policies.appsensor import MiscSensor
from tcell_agent.policies.appsensor import RequestSizeSensor
from tcell_agent.policies.appsensor import ResponseCodesSensor
from tcell_agent.policies.appsensor import ResponseSizeSensor
from tcell_agent.policies.appsensor import UserAgentSensor
from tcell_agent.policies.appsensor_policy import AppSensorPolicy

policy_one = """
{
    "policy_id":"abc-abc-abc",
    "data": {
        "options": {
            "xss":true
        }
    }
}
"""

policy_v2_req_size = """
{
    "policy_id":"abc-abc-abc",
    "version":2,
    "data": {
        "options": {
            "payloads": {}
        },
        "sensors": {
            "req_size": {
                "limit":1024,
                "exclude_routes":["2300"]
            }
        }
    }
}
"""

policy_v2_all_options = """
{
    "policy_id":"abc-abc-abc",
    "version":2,
    "data": {
        "options": {
            "payloads": {}
        },
        "sensors": {
            "req_size": {
                "limit":1024,
                "exclude_routes":["2300"]
            },
            "resp_size": {
                "limit":2048,
                "exclude_routes":["2323"]
            },
            "resp_codes": {
                "series_400_enabled":true,
                "series_500_enabled":true
            },
            "xss": {
                "libinjection":true,
                "patterns":["1","2","8"],
                "exclusions":{
                    "bob":["*"]
                }
            },
            "sqli":{
                "libinjection":true,
                "exclude_headers":true,
                "patterns":["1"]
            },
            "fpt":{
                "patterns":["1","2"],
                "exclude_forms":true,
                "exclude_cookies":true,
                "exclusions":{
                    "somethingcommon":["form"]
                }
            },
            "cmdi":{
                 "patterns":["1","2"]
            },
            "nullbyte":{
                 "patterns":["1","2"]
            },
            "retr":{
                "patterns":["1","2"]
            },
            "ua": {
                "empty_enabled": true
            },
            "login":{
                "lgnSccss_enabled":true,
                "lgnFlr_enabled":true,
                "psswdRstReq":true,
                "psswdRstAttmpt":true,
                "psswdRst":true
            },
            "errors":{
                "csrf_exception_enabled": true,
                "sql_exception_enabled": true
            }
        }
    }
}
"""

class AppSensorPolicyTest(unittest.TestCase):
    def classname_test(self):
        self.assertEqual(AppSensorPolicy.api_identifier, "appsensor")

    def read_appensor_v1_policy_test(self):
        policy_json = json.loads(policy_one)
        policy = AppSensorPolicy()
        policy.loadFromJson(policy_json)

        self.assertIsNotNone(policy.options["req_size"])
        self.assertIsNotNone(policy.options["resp_size"])
        self.assertIsNotNone(policy.options["resp_codes"])
        self.assertIsNotNone(policy.options["xss"])
        self.assertIsNotNone(policy.options["sqli"])
        self.assertIsNotNone(policy.options["cmdi"])
        self.assertIsNotNone(policy.options["fpt"])
        self.assertIsNotNone(policy.options["nullbyte"])
        self.assertIsNotNone(policy.options["retr"])
        self.assertIsNotNone(policy.options["login"])
        self.assertIsNotNone(policy.options["ua"])
        self.assertIsNotNone(policy.options["errors"])

        self.assertFalse(policy.options["req_size"].enabled)
        self.assertFalse(policy.options["resp_size"].enabled)
        self.assertFalse(policy.options["resp_codes"].enabled)
        self.assertTrue(policy.options["xss"].enabled)
        self.assertFalse(policy.options["cmdi"].enabled)
        self.assertFalse(policy.options["fpt"].enabled)
        self.assertFalse(policy.options["nullbyte"].enabled)
        self.assertFalse(policy.options["retr"].enabled)
        self.assertFalse(policy.options["login"].enabled)
        self.assertFalse(policy.options["ua"].enabled)
        self.assertFalse(policy.options["errors"].csrf_exception_enabled)
        self.assertFalse(policy.options["errors"].sql_exception_enabled)

        self.assertTrue(policy.options["resp_codes"].series_400_enabled)
        self.assertTrue(policy.options["resp_codes"].series_500_enabled)

        self.assertTrue(policy.options["xss"].v1_compatability_enabled)
        self.assertTrue(policy.options["sqli"].v1_compatability_enabled)
        self.assertTrue(policy.options["cmdi"].v1_compatability_enabled)
        self.assertTrue(policy.options["fpt"].v1_compatability_enabled)
        self.assertTrue(policy.options["nullbyte"].v1_compatability_enabled)
        self.assertTrue(policy.options["retr"].v1_compatability_enabled)


    def read_appensor_v2_req_size_policy_test(self):
        policy_json = json.loads(policy_v2_req_size)
        policy = AppSensorPolicy()
        policy.loadFromJson(policy_json)

        self.assertIsNotNone(policy.options["req_size"])
        self.assertIsNotNone(policy.options["resp_size"])
        self.assertIsNotNone(policy.options["resp_codes"])
        self.assertIsNotNone(policy.options["xss"])
        self.assertIsNotNone(policy.options["sqli"])
        self.assertIsNotNone(policy.options["cmdi"])
        self.assertIsNotNone(policy.options["fpt"])
        self.assertIsNotNone(policy.options["nullbyte"])
        self.assertIsNotNone(policy.options["retr"])
        self.assertIsNotNone(policy.options["login"])
        self.assertIsNotNone(policy.options["ua"])
        self.assertIsNotNone(policy.options["errors"])

        self.assertTrue(policy.options["req_size"].enabled)
        self.assertFalse(policy.options["resp_size"].enabled)
        self.assertFalse(policy.options["resp_codes"].enabled)
        self.assertFalse(policy.options["xss"].enabled)
        self.assertFalse(policy.options["cmdi"].enabled)
        self.assertFalse(policy.options["fpt"].enabled)
        self.assertFalse(policy.options["nullbyte"].enabled)
        self.assertFalse(policy.options["retr"].enabled)
        self.assertFalse(policy.options["login"].enabled)
        self.assertFalse(policy.options["ua"].enabled)
        self.assertFalse(policy.options["errors"].csrf_exception_enabled)
        self.assertFalse(policy.options["errors"].sql_exception_enabled)

    def read_appensor_v2_all_options_policy_test(self):
        policy_json = json.loads(policy_v2_all_options)
        policy = AppSensorPolicy()

        policy.loadFromJson(policy_json)

        self.assertIsNotNone(policy.options["req_size"])
        self.assertIsNotNone(policy.options["resp_size"])
        self.assertIsNotNone(policy.options["resp_codes"])
        self.assertIsNotNone(policy.options["xss"])
        self.assertIsNotNone(policy.options["sqli"])
        self.assertIsNotNone(policy.options["cmdi"])
        self.assertIsNotNone(policy.options["fpt"])
        self.assertIsNotNone(policy.options["nullbyte"])
        self.assertIsNotNone(policy.options["retr"])
        self.assertIsNotNone(policy.options["login"])
        self.assertIsNotNone(policy.options["ua"])
        self.assertIsNotNone(policy.options["errors"])

        self.assertTrue(policy.options["req_size"].enabled)
        self.assertTrue(policy.options["resp_size"].enabled)
        self.assertTrue(policy.options["resp_codes"].enabled)
        self.assertTrue(policy.options["xss"].enabled)
        self.assertTrue(policy.options["cmdi"].enabled)
        self.assertTrue(policy.options["fpt"].enabled)
        self.assertTrue(policy.options["nullbyte"].enabled)
        self.assertTrue(policy.options["retr"].enabled)
        self.assertTrue(policy.options["login"].enabled)
        self.assertTrue(policy.options["ua"].enabled)
        self.assertTrue(policy.options["ua"].empty_enabled)
        self.assertTrue(policy.options["errors"].csrf_exception_enabled)
        self.assertTrue(policy.options["errors"].sql_exception_enabled)

    def test_run_for_response(self):
        policy_json = json.loads(policy_v2_all_options)
        policy = AppSensorPolicy()
        policy.loadFromJson(policy_json)

        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "route_id",
            session_id="session_id",
            user_id="user_id"
        )

        meta.response_data(1024, 200)

        with patch.object(ResponseSizeSensor, 'check') as patched_size_check:
            with patch.object(ResponseCodesSensor, 'check') as patched_codes_check:
                policy.run_for_response(meta)
                patched_size_check.assert_called_once_with(meta, 1024)
                patched_codes_check.assert_called_once_with(meta, 200)

    def test_check_login_failure(self):
        policy_json = json.loads(policy_v2_all_options)
        policy = AppSensorPolicy()
        policy.loadFromJson(policy_json)

        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "route_id",
            session_id="session_id",
            user_id="user_id"
        )

        with patch.object(LoginSensor, 'check') as patched_check:
            policy.check_login_failure(meta, "username")
            patched_check.assert_called_once_with(meta, "username")

    def test_run_for_request_with_no_params(self):
        policy_json = json.loads(policy_v2_all_options)
        policy = AppSensorPolicy()
        policy.loadFromJson(policy_json)

        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "route_id",
            session_id="session_id",
            user_id="user_id"
        )

        meta.request_data(1024)

        with patch.object(RequestSizeSensor, 'check') as patched_check:
            with patch.object(InjectionSensor, 'check') as patched_injection_check:
                with patch.object(UserAgentSensor, 'check') as patched_ua_check:
                    policy.run_for_request(meta, {})
                    patched_check.assert_called_once_with(meta, 1024)
                    patched_ua_check.assert_called_once_with(meta)
                    self.assertFalse(patched_injection_check.called)

    def test_csrf_rejected(self):
        policy_json = json.loads(policy_v2_all_options)
        policy = AppSensorPolicy()
        policy.loadFromJson(policy_json)

        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "route_id",
            session_id="session_id",
            user_id="user_id"
        )

        with patch.object(MiscSensor, 'csrf_rejected') as patched_csrf_rejected:
            policy.csrf_rejected(meta, "Missing CSRF")
            patched_csrf_rejected.assert_called_once_with(meta, "Missing CSRF")
