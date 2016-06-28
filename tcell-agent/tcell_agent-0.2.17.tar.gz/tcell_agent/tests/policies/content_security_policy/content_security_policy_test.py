from __future__ import unicode_literals
from __future__ import print_function

import unittest
from ....policies.content_security_policy import ContentSecurityPolicy
from ....policies.content_security_policy import java_hash
import re

import json

from future.backports.urllib.parse import urlparse
from future.backports.urllib.parse import parse_qs

policy_one = """
{
    "policy_id":"abc-abc-abc",
    "headers":[],
    "data": {
      "options":{
        "js_agent_api_key":"000-000-1"
      }
    }
}
"""

class ContentSecurityPolicyTest(unittest.TestCase):
    def old_header_test(self):
        policy = ContentSecurityPolicy()
        policy.loadFromHeaderString("Content-Security-Policy-Report-Only: test123")
        self.assertEqual(policy.headers(), [['Content-Security-Policy-Report-Only', ' test123']])

    def new_header_test(self):
        policy_json = {"policy_id":"xyzd", "headers":[{"name":"content-Security-POLICY", "value":"test321"}]}
        policy = ContentSecurityPolicy()
        policy.loadFromJson(policy_json)
        self.assertEqual(policy.headers(), [['Content-Security-Policy', 'test321']])

    def header_with_report_uri_test(self):
        policy_json = {"policy_id":"xyzd", 
                       "headers":[{"name":"content-Security-policy", "value":"normalvalue","report-uri":"https://www.example.com/xys"}]
                      }
        policy = ContentSecurityPolicy()
        policy.loadFromJson(policy_json)
        policy_headers = policy.headers("1","2","3")
        policy_header = policy_headers[0]
        print(policy_header)
        self.assertEqual(policy_header[0],"Content-Security-Policy")
        policy_header_value_parts = urlparse(policy_header[1].split(" ")[2])
        self.assertEqual(policy_header_value_parts.path, "/xys")
        print(policy_header_value_parts.query)
        query_params = parse_qs(policy_header_value_parts.query)
        print(query_params)
        self.assertEqual(query_params["tid"], ["1"])
        self.assertEqual(query_params["rid"], ["2"])
        self.assertEqual(query_params["sid"], ["3"])
        fromstr = policy_header[1].split(" ")[2]
        check_against = policy.policy_id + re.match("(.*)&c=[a-zA-Z0-9\-]+$", fromstr).group(1)
        self.assertEqual(query_params["c"], [str(java_hash(check_against))])

    def check_java_hash_test(self):
        base_str = "What the heck?"
        self.assertEqual(str(java_hash(base_str)), "277800975")
        self.assertEqual(str(java_hash("https://example.com/abcdde?tid=1&sid=3&rid=2")), "947858466")
        self.assertEqual(str(java_hash("Hello World")), "-862545276")

    def handle_js_agent_add(self):
        policy_json = json.loads(policy_one)
        policy = ContentSecurityPolicy()
        self.assertEqual(policy.js_agent_api_key, "000-000-1")

