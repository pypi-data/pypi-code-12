from dbaas_aclapi import helpers
import unittest
from tests.factory import AclApiTestCase, Request


class TaskHelpersTest(AclApiTestCase):
    def test_build_data_default_options_dict(self):
        action = 'permit'
        bind_address = '10.253.1.5'
        database_name = 'mysql_test'
        database_environment = 'dev'

        description = "{} {} access for database {} in {}".format(
            action, bind_address, database_name, database_environment)

        data = {"kind": "object#acl", "rules": []}
        default_options = {"protocol": "tcp",
                           "source": "",
                           "destination": "",
                           "description": description,
                           "action": action,
                           "l4-options": {"dest-port-start": "",
                                          "dest-port-op": "eq"}
                           }
        r_data, r_default_options = helpers.build_data_default_options_dict(
            action, bind_address, database_name, database_environment)

        self.assertEqual(data, r_data)
        self.assertEqual(default_options, r_default_options)

    def test_iter_on_acl_query_results(self):
        query_gen = helpers.iter_on_acl_query_results(
            self.acl_api_client, {"test": "test"})
        for environment_id, vlan_id, rule_id in query_gen:
            self.assertEqual(environment_id, '13912')
            self.assertEqual(vlan_id, '8')
            self.assertEqual(rule_id, '98920')

    @unittest.skip("Must fix import")
    def test_get_user_from_param(self):
        user = helpers.get_user('test', 'admin', 'permit')
        self.assertEqual(user, 'admin')

    @unittest.skip("Must fix import")
    def test_get_user_from_request(self):
        request = Request('root')
        user = helpers.get_user(request, None, 'permit')
        self.assertEqual(user, 'root')

    def tearDown(self):
        pass
