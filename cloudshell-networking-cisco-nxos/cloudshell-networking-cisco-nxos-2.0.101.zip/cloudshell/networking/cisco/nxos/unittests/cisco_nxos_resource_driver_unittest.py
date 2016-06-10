from unittest import TestCase
import inject
from mock import Mock
from cloudshell.networking.cisco.nxos.cisco_nxos_resource_driver import CiscoNXOSDriver
import types
from cloudshell.shell.core.context import AutoLoadCommandContext


class CiscoNXOSDriverUnitTest(TestCase):

    def setUp(self):
        config = types.ModuleType('config')

        handler_mock = Mock()
        config.HANDLER_CLASS = lambda : handler_mock

        logger_mock = Mock()
        logger_mock.info = Mock()
        logger_mock.error = Mock()
        logger_mock.debug = Mock()
        config.GET_LOGGER_FUNCTION = lambda : logger_mock

        def test_bindings(binder):
            binder.bind('cli_service', Mock())

        self.driver = CiscoNXOSDriver(config, test_bindings)

    def test_initialize(self):
        #Arrange
        self.driver.initialize = Mock()
        #Act
        result = self.driver.initialize()
        #Assert
        self.assertTrue(result, 'Finished initializing')

    def test_simple_command(self):
        #Arrange
        handler = inject.instance('handler')
        handler.send_command = Mock(return_value="show ver output")
        command = Mock(return_value="show ver")
        #Act
        result = self.driver.simple_command(command)
        #Assert
        self.assertTrue(handler.send_command.called)

    def test_get_inventory(self):
        #Arrange
        # print(type(self.driver))
        # handler = Mock()
        handler = inject.instance('handler')
        handler.discover_snmp = Mock()
        logger = inject.instance('logger')
        logger.info = Mock()
        context = Mock(spec=AutoLoadCommandContext)
        context.resource = Mock()
        context.resource.name = Mock(return_value="resource name")
        #Act
        self.driver.get_inventory(context)
        #Assert
        self.assertTrue(handler.discover_snmp.called)
        pass

    def test_load_firmware(self):
        #Arrange
        handler = inject.instance('handler')
        handler.update_firmware = Mock()
        context = Mock(spec=AutoLoadCommandContext)
        context.resource = Mock()
        context.resource.name = Mock(return_value="resource name")
        remote_host = Mock(return_value="127.0.0.1")
        file_path = Mock(return_value="/tmp/file")
        #Act
        self.driver.load_firmware(context, remote_host, file_path)
        #Assert
        self.assertTrue(handler.update_firmware.called)

    def test_save(self):
        #Arrange
        handler = inject.instance('handler')
        handler.save_configuration = Mock()
        context = Mock(spec=AutoLoadCommandContext)
        context.resource = Mock()
        context.resource.name = Mock(return_value="resource name")
        folder_path = Mock(return_value="test_folder")
        configuration_type = Mock(return_value="running")
        #Act
        self.driver.save(context, folder_path, configuration_type)
        #Assert
        self.assertTrue(handler.save_configuration.called)
        pass

    def test_restore(self):
        #Arrange
        handler = inject.instance('handler')
        handler.restore_configuration = Mock()
        context = Mock(spec=AutoLoadCommandContext)
        context.resource = Mock()
        context.resource.name = Mock(return_value="resource name")
        path = Mock(return_value="test_folder")
        configuration_type = Mock(return_value="running")
        restore_method = Mock(return_value="append")
        #Act
        self.driver.restore(context, path, configuration_type, restore_method)
        #Assert
        self.assertTrue(handler.restore_configuration.called)

    def test_send_custom_command(self):
        #Arrange
        cli = inject.instance("cli_service")
        cli.send_command = Mock()
        context = Mock(spec=AutoLoadCommandContext)
        context.resource = Mock()
        context.resource.name = Mock(return_value="resource name")
        command = Mock(return_value="sample command")
        #Act
        self.driver.send_custom_command(context, command)
        #Assert
        self.assertTrue(cli.send_command.called)
        pass

    def test_add_vlan(self):
        #Arrange
        handler = inject.instance('handler')
        handler.add_vlan = Mock()
        context = Mock(spec=AutoLoadCommandContext)
        context.resource = Mock()
        context.resource.name = Mock(return_value="resource name")
        ports = 0
        vlan_range = "500-1000"
        port_mode = 'trunk'
        additional_info = "info"
        #Act
        self.driver.add_vlan(context, ports, vlan_range, port_mode, additional_info)
        #Assert
        self.assertTrue(handler.add_vlan.called)

    def test_remove_vlan(self):
        #Arrange
        handler = inject.instance('handler')
        handler.remove_vlan = Mock()
        context = Mock(spec=AutoLoadCommandContext)
        context.resource = Mock()
        context.resource.name = Mock(return_value="resource name")
        ports = 0
        vlan_range = "500-1000"
        port_mode = 'trunk'
        additional_info = "info"
        #Act
        self.driver.remove_vlan(context, ports, vlan_range, port_mode, additional_info)
        #Assert
        self.assertTrue(handler.remove_vlan.called)

    def test_send_custom_config_command(self):
        #Arrange
        handler = inject.instance('handler')
        handler.sendConfigCommand = Mock()
        context = Mock(spec=AutoLoadCommandContext)
        context.resource = Mock()
        context.resource.name = Mock(return_value="resource name")
        command = Mock(return_value="test command")
        #Act
        self.driver.send_custom_config_command(context, command)
        #Assert
        self.assertTrue(handler.sendConfigCommand.called)