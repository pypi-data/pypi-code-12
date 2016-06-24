from __future__ import unicode_literals
from __future__ import print_function

import json
import unittest

from nose.tools import raises

from tcell_agent.policies import PatchesPolicy

class AppSensorPolicyTest(unittest.TestCase):
    def classname_test(self):
        self.assertEqual(PatchesPolicy.api_identifier, "patches")

    def none_policy_test(self):
        policy = PatchesPolicy()

        self.assertIsNone(policy.policy_id)
        self.assertIsNone(policy.version)
        self.assertFalse(policy.ip_blocking_enabled)
        self.assertEqual(policy.blocked_ips, {})

    @raises(Exception)
    def empty_policy_test(self):
        policy = PatchesPolicy({})

    def empty_version_policy_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id"
        })

        self.assertEqual(policy.policy_id, "policy_id")
        self.assertIsNone(policy.version)
        self.assertFalse(policy.ip_blocking_enabled)
        self.assertEqual(policy.blocked_ips, {})

    def empty_data_policy_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {}
        })

        self.assertEqual(policy.policy_id, "policy_id")
        self.assertEqual(policy.version, 1)
        self.assertFalse(policy.ip_blocking_enabled)
        self.assertEqual(policy.blocked_ips, {})

    def empty_blocked_ips_policy_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "blocked_ips": []
            }
        })

        self.assertEqual(policy.policy_id, "policy_id")
        self.assertEqual(policy.version, 1)
        self.assertFalse(policy.ip_blocking_enabled)
        self.assertEqual(policy.blocked_ips, {})

    def populated_blocked_ips_policy_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "blocked_ips": [{
                    "ip": "1.1.1.1"
                }]
            }
        })

        self.assertEqual(policy.policy_id, "policy_id")
        self.assertEqual(policy.version, 1)
        self.assertTrue(policy.ip_blocking_enabled)
        self.assertEqual(policy.blocked_ips, {"1.1.1.1": True})

    def populated_blocked_ips_with_wrong_version_policy_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 2,
            "data": {
                "blocked_ips": [{
                    "ip": "1.1.1.1"
                }]
            }
        })

        self.assertEqual(policy.policy_id, "policy_id")
        self.assertEqual(policy.version, 2)
        self.assertFalse(policy.ip_blocking_enabled)
        self.assertEqual(policy.blocked_ips, {})

    def populated_blocked_ips_with_missing_ip_policy_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "blocked_ips": [{
                    "ip_wrong": "1.1.1.1"
                }]
            }
        })

        self.assertEqual(policy.policy_id, "policy_id")
        self.assertEqual(policy.version, 1)
        self.assertFalse(policy.ip_blocking_enabled)
        self.assertEqual(policy.blocked_ips, {})

    def disabled_ip_blocking_is_ip_blocked_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
            }
        })

        self.assertFalse(policy.is_ip_blocked("1.1.1.1"))

    def enabled_ip_blocking_is_ip_blocked_with_none_ip_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "blocked_ips": [{
                    "ip": "1.1.1.1"
                }]
            }
        })

        self.assertFalse(policy.is_ip_blocked(None))

    def enabled_ip_blocking_is_ip_blocked_with_empty_ip_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "blocked_ips": [{
                    "ip": "1.1.1.1"
                }]
            }
        })

        self.assertFalse(policy.is_ip_blocked(""))

    def enabled_ip_blocking_is_ip_blocked_with_blocked_ip_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "blocked_ips": [{
                    "ip": "1.1.1.1"
                }]
            }
        })

        self.assertTrue(policy.is_ip_blocked("1.1.1.1"))

    def enabled_ip_blocking_is_ip_blocked_with_non_blocked_ip_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "blocked_ips": [{
                    "ip": "1.1.1.1"
                }]
            }
        })

        self.assertFalse(policy.is_ip_blocked("2.2.2.2"))
