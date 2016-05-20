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

    def override_get_ruleset_test(self):
        with patch.object(AppSensorRuleManager, 'get_ruleset_for', return_value=None) as patched_get_ruleset_for:
            sensor = NullbyteSensor()
            sensor.get_ruleset()
            patched_get_ruleset_for.assert_called_once_with('nullbyte')
