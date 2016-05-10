# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function

import unittest
import re
from ....policies.http_redirect_policy import HttpRedirectPolicy

class HttpRedirectPolicyTest(unittest.TestCase):
    def min_header_test(self):
        policy_json = {"policy_id":"xyzd"}
        policy = HttpRedirectPolicy()
        policy.loadFromJson(policy_json)
        self.assertEqual(policy.policy_id, "xyzd")
        self.assertEqual(policy.enabled, False)
        self.assertEqual(policy.block, False)
        self.assertEqual(policy.whitelist, [])

    def small_header_test(self):
        policy_json = {"policy_id":"nyzd", "data":{"enabled":True}}
        policy = HttpRedirectPolicy()
        policy.loadFromJson(policy_json)
        self.assertEqual(policy.policy_id, "nyzd")
        self.assertEqual(policy.enabled, True)
        self.assertEqual(policy.block, False)
        self.assertEqual(policy.whitelist, [])

    def large_header_test(self):
        policy_json = {"policy_id":"nyzd", 
                       "data":{
                            "enabled":True,
                            "whitelist":["whitelisted"],
                            "block":True
                        }
                       } 
        policy = HttpRedirectPolicy()
        policy.loadFromJson(policy_json)
        self.assertEqual(policy.policy_id, "nyzd")
        self.assertEqual(policy.enabled, True)
        self.assertEqual(policy.block, True)
        whitelist = ["whitelisted"]
        compiled_re = [policy.wildcard_re(item) for item in whitelist]
        self.assertEqual(policy.whitelist, compiled_re)

    def same_domain_redirect_test(self):
        policy_json = {"policy_id":"nyzd", 
                       "data":{
                            "enabled":True,
                            "whitelist":["whitelisted"],
                            "block":True
                        }
                       } 
        policy = HttpRedirectPolicy()
        policy.loadFromJson(policy_json)
        self.assertEqual(policy.policy_id, "nyzd")
        self.assertEqual(policy.enabled, True)
        self.assertEqual(policy.block, True)
        whitelist = ["whitelisted"]
        compiled_re = [policy.wildcard_re(item) for item in whitelist]
        self.assertEqual(policy.whitelist, compiled_re)

        check = policy.process_location( 
            "0.1.1.0",
            "GET",
            "localhost:8011",
            "/etc/123",
            200,
            "http://localhost:8011/abc/def")
        print(check)
        self.assertEqual(check,"http://localhost:8011/abc/def")