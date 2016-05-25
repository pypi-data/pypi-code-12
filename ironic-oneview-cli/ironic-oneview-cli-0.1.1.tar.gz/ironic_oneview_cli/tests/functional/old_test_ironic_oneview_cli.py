# -*- encoding: utf-8 -*-
#
# Copyright 2015 Hewlett-Packard Development Company, L.P.
# Copyright 2015 Universidade Federal de Campina Grande
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
test_ironic-oneview-cli
----------------------------------

Tests for `ironic-oneview-cli` module.
"""
import mock
import time

from ironic_oneview_cli import common
from ironic_oneview_cli.import config
from ironic_oneview_cli import openstack_client
from ironic_oneview_cli.create_flavor_shell import commands as flavor_commands
from ironic_oneview_cli.create_flavor_shell import objects
from ironic_oneview_cli.create_node_shell import commands as node_commands
from ironic_oneview_cli import facade
from ironic_oneview_cli.tests import base


def delay(delay_time):
    time.sleep(delay_time)


@mock.patch.object(common, 'get_oneview_client')
@mock.patch.object(openstack_client, 'get_ironic_client')
@mock.patch.object(openstack_client, 'get_nova_client')
class TestIronicOneviewCLI(base.TestCase):

    def setUp(self):
        self.config = config.ConfClient()
        self.facade = facade.Facade(self.config)

    def test_list_server_hardware_not_enrolled(self,
                                               mock_nova_cli,
                                               mock_ironic_cli,
                                               mock_ov_cli):
        node_creator = node_commands.NodeCreator(self.config)
        all_sh = self.facade.list_server_hardware_available()
        node_creator.list_server_hardware_not_enrolled(all_sh)
        self.assert_called_once_with(mock_ov_cli.server_hardware.list, {})
        self.assert_called_once_with(mock_ironic_cli.node.list, detail=True)

    def test_list_server_hardware_not_enrolled_with_one_sh_already_created(
        self,
        mock_nova_cli,
        mock_ironic_cli,
        mock_ov_cli
    ):
        node_creator = node_commands.NodeCreator(self.config)
        server_hardwares_not_created = (
            node_creator.list_server_hardware_not_enrolled(
                self.facade.list_server_hardware_available()
            )
        )
        available_sh_count = len(server_hardwares_not_created)
        compatible_templates = self.facade.list_templates_compatible_with(
            server_hardwares_not_created
        )

        node = node_creator.create_node(server_hardwares_not_created[0],
                                        compatible_templates[0])
        server_hardwares_not_enrolled = (
            node_creator.list_server_hardware_not_enrolled(
                self.facade.list_server_hardware_available()
            )
        )
        new_available_sh_count = len(server_hardwares_not_enrolled)
        self.assertEqual(new_available_sh_count, (available_sh_count - 1))
        self.ironic_client.node.delete(node.uuid)

    def test_create_one_node(self,
                             mock_nova_cli,
                             mock_ironic_cli,
                             mock_ov_cli):
        node_creator = NodeCreator(self.config)
        server_hardwares_not_created = (
            node_creator.list_server_hardware_not_enrolled(
                self.facade.list_server_hardware_available()
            )
        )
        available_sh_count = len(server_hardwares_not_created)
        compatible_templates = self.facade.list_templates_compatible_with(
            server_hardwares_not_created
        )

        node = node_creator.create_node(server_hardwares_not_created[0],
                                        compatible_templates[0])
        self.created_nodes.append(node.uuid)
        server_hardwares_not_created = (
            node_creator.list_server_hardware_not_enrolled(
                self.facade.list_server_hardware_available()
            )
        )
        new_available_sh_count = len(server_hardwares_not_created)
        self.assertEqual(new_available_sh_count, (available_sh_count - 1))
        ironic_node_list = self.ironic_client.node.list()
        node_was_created = False
        for ironic_node in ironic_node_list:
            if ironic_node.uuid == node.uuid:
                node_was_created = True
                break
        self.assertEqual(node_was_created, True)

    def test_get_flavor_name(self):
        flavor_info = {'cpu_arch': 'x64', 'ram_mb': '32000',
                       'cpus': '8', 'disk': '120'}
        flavor = Flavor(1, flavor_info)
        flavor_name = flavor_commands._get_flavor_name(flavor)
        self.assertEqual('32000MB-RAM_8_x64_120', flavor_name)

    def test_get_flavor_from_ironic_node(self):
        server_hardwares_not_created = (
            self.node_creator.list_server_hardware_not_enrolled(
                self.facade.list_server_hardware_available()
            )
        )
        server_hardware_for_test = server_hardwares_not_created[0]
        compatible_templates = (
            self.facade.list_templates_compatible_with(
                server_hardwares_not_created
            )
        )
        node = self.node_creator.create_node(server_hardware_for_test,
                                             compatible_templates[0])
        server_profile_for_test = compatible_templates[0]
        flavor = flavor_commands.get_flavor_from_ironic_node(
            1,
            node,
            self.facade
        )
        self.assertEqual(server_hardware_for_test.memory_mb, flavor.ram_mb)
        self.assertEqual(server_hardware_for_test.cpus, flavor.cpus)
        self.assertEqual(120, flavor.disk)
        self.assertEqual(server_hardware_for_test.cpu_arch, flavor.cpu_arch)
        self.assertEqual(server_hardware_for_test.server_hardware_type.uri,
                         flavor.server_hardware_type_uri)
        self.assertEqual(server_hardware_for_test.enclosure_group_uri,
                         flavor.enclosure_group_uri)
        self.assertEqual(server_profile_for_test.uri,
                         flavor.server_profile_template_uri)

    def test_create_node_retrieve_n_check(self):
        node_creator = NodeCreator(self.config)
        server_hardwares_not_created = (
            node_creator.list_server_hardware_not_enrolled(
                self.facade.list_server_hardware_available()
            )
        )
        hardware_selected = server_hardwares_not_created[0]
        compatible_templates = self.facade.list_templates_compatible_with(
            server_hardwares_not_created
        )
        template_selected = compatible_templates[0]

        node = node_creator.create_node(hardware_selected, template_selected)
        self.created_nodes.append(node.uuid)

        self.assertEqual(node.driver_info.get('server_hardware_uri'),
                         hardware_selected.uri)
        self.assertEqual(node.driver_info.get('deploy_kernel'),
                         self.config.ironic.default_deploy_kernel_id)
        self.assertEqual(node.driver_info.get('deploy_ramdisk'),
                         self.config.ironic.default_deploy_ramdisk_id)
        capabilities = node.properties.get('capabilities')
        self.assertIn('server_profile_template_uri:' + template_selected.uri,
                      capabilities)

    def test_create_flavor_with_server_hadware_type_enclosure_group_server_profile_template_name_is_not_empty(self):
        flavors = flavor_commands.get_flavor_list(self.ironic_client,
                                                  self.facade)
        for flavor in flavors:
            self.assertNotEqual("", flavor['server_hardware_type_name'])
            self.assertNotEqual("", flavor['enclosure_group_name'])
            self.assertNotEqual("", flavor['server_profile_template_name'])

    def test_create_flavor_with_server_hadware_type_enclosure_group_server_profile_template_name_is_not_none(self):
        flavors = flavor_commands.get_flavor_list(self.ironic_client,
                                                  self.facade)
        for flavor in flavors:
            self.assertIsNotNone(flavor['server_hardware_type_name'])
            self.assertIsNotNone(flavor['enclosure_group_name'])
            self.assertIsNotNone(flavor['server_profile_template_name'])


if __name__ == '__main__':
    base.main()
