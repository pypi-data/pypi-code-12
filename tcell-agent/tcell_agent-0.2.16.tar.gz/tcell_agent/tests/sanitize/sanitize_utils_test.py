from __future__ import unicode_literals
from __future__ import print_function
import unittest
from ...sanitize.sanitize_utils import SanitizeUtils
from ...config import CONFIGURATION


class SanitizerUtilsTest(unittest.TestCase):
    def old_header_test(self):
        CONFIGURATION.app_id = None
        response_info = {}
        response_info["headers"] = {"set-cookie":["sessionToken=abc123; Expires=Wed, 09 Jun 2021 10:18:14 GMT"]}
        SanitizeUtils.sanitize_response_info(response_info)
        self.assertEqual(response_info["headers"]["set-cookie"], ['sessionToken=8aed87a14d7369b35600b3eb61d24e51dab0fe083749b270acb9be31603da8d6; expires=Wed, 09 Jun 2021 10:18:14 GMT'])

    def request_sanitize_test(self):
        CONFIGURATION.app_id = None
        request_info = {}
        request_info["uri"] = "/abc/def"
        request_info["headers"] = {"cookie":["sessionToken=abc123; sessionToken2=sdfdsf"]}
        SanitizeUtils.sanitize_request_info(request_info)
        self.assertEqual(request_info["headers"]["cookie"], [' sessionToken=8aed87a14d7369b35600b3eb61d24e51dab0fe083749b270acb9be31603da8d6; sessionToken2=6255969f6b578c815cc57426ad8520f5480eff23bb9f632720a38d2b2c9429aa'])

    def strip_uri_test(self):
        CONFIGURATION.app_id = None
        self.assertEqual(SanitizeUtils.strip_uri("/abc/def?bbb=abcd"),"/abc/def?bbb=")
        self.assertEqual(SanitizeUtils.strip_uri("https://aaa:8000/abc/def?bbb=ccbc"),"https://aaa:8000/abc/def?bbb=")