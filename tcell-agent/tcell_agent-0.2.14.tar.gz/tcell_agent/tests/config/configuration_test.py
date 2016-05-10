# -*- coding: utf-8 -*-

from tcell_agent.config import TcellAgentConfiguration

import unittest
from ...agent import TCellAgent
import os

class TcellAgentConfigurationTest(unittest.TestCase):
    def test_default_blacklisted_parameters(self):
        configuration = TcellAgentConfiguration()

        self.assertEqual(configuration.blacklisted_params, {
            'client_secret': True,
            'passwd': True,
            'password': True,
            'pf.pass': True,
            'refresh_token': True,
            'token': True,
            'user.password': True})
        self.assertEqual(configuration.whitelisted_params, {})
        self.assertFalse(configuration.whitelist_present)

    def test_specifying_blacklisted_parameters(self):
        full_path = os.path.realpath(__file__)
        blacklist_config = os.path.join(os.path.dirname(full_path), "blacklist_payload.config")
        os.environ["TCELL_AGENT_PAYLOADS_CONFIG"] = blacklist_config
        configuration = TcellAgentConfiguration()

        self.assertEqual(configuration.blacklisted_params, {'foo': True})
        self.assertEqual(configuration.whitelisted_params, {})
        self.assertFalse(configuration.whitelist_present)

    def test_specifying_whitelisted_parameters(self):
        full_path = os.path.realpath(__file__)
        whitelist_config = os.path.join(os.path.dirname(full_path), "whitelist_payload.config")
        os.environ["TCELL_AGENT_PAYLOADS_CONFIG"] = whitelist_config
        configuration = TcellAgentConfiguration()

        self.assertEqual(configuration.blacklisted_params, {
            'client_secret': True,
            'passwd': True,
            'password': True,
            'pf.pass': True,
            'refresh_token': True,
            'token': True,
            'user.password': True})
        self.assertEqual(configuration.whitelisted_params, {'foo': True})
        self.assertTrue(configuration.whitelist_present)

    def test_setting_max_data_ex_db_records_per_request(self):
        full_path = os.path.realpath(__file__)
        data_exposure_config = os.path.join(os.path.dirname(full_path), "data_exposure.config")
        configuration = TcellAgentConfiguration(data_exposure_config)

        self.assertEqual(configuration.max_data_ex_db_records_per_request, 100)

