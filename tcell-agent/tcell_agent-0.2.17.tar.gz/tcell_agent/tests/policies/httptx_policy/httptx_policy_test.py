from __future__ import unicode_literals
from __future__ import print_function

import unittest
from ....policies.httptx_policy import HttpTxPolicy

class HttpTxPolicyTest(unittest.TestCase):
    def min_header_test(self):
        policy_json = {"policy_id":"xyzd"}
        policy = HttpTxPolicy()
        policy.loadFromJson(policy_json)
        self.assertEqual(policy.policy_id, "xyzd")
        self.assertEqual(policy.firehose["enabled"], False)

    def new_header_test(self):
        policy_json = {"policy_id":"nyzd", "types":{"firehose":{"enabled":True}}}
        policy = HttpTxPolicy()
        policy.loadFromJson(policy_json)
        self.assertEqual(policy.policy_id, "nyzd")
        self.assertEqual(policy.firehose["enabled"], True)
