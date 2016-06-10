from cloudshell.networking.generic_bootstrap import NetworkingGenericBootstrap
from cloudshell.networking.networking_resource_driver_interface import NetworkingResourceDriverInterface
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.context_utils import context_from_args
import cloudshell.networking.cisco.nxos.cisco_nxos_configuration as config
import inject


class CiscoNXOSDriver(ResourceDriverInterface, NetworkingResourceDriverInterface):
    def __init__(self):
        bootstrap = NetworkingGenericBootstrap()
        bootstrap.add_config(config)
        bootstrap.initialize()

    @context_from_args
    def initialize(self, context):
        """
        :type context: cloudshell.shell.core.driver_context.InitCommandContext
        """
        return 'Finished initializing'

    # Destroy the driver session, this function is called everytime a driver instance is destroyed
    # This is a good place to close any open sessions, finish writing to log files
    def cleanup(self):
        pass

    @context_from_args
    def get_inventory(self, context):
        """
        Return device structure with all standard attributes
        :return: result
        :rtype: string
        """
        handler = inject.instance("handler")
        result = handler.discover_snmp()
        return result

    @context_from_args
    def update_firmware(self, context, remote_host, file_path):
        """
        Upload and updates firmware on the resource
        :return: result
        :rtype: string
        """
        handler = inject.instance("handler")
        result_str = handler.update_firmware(remote_host=remote_host, file_path=file_path)
        handler.logger.info(result_str)

    @context_from_args
    def restore(self, context, path, config_type, restore_method, vrf=None):
        """Restore selected file to the provided destination

        :param path: source config file
        :param config_type: running or startup configs
        :param restore_method: append or override methods
        :param vrf: VRF management Name
        """

        handler = inject.instance('handler')
        response = handler.restore_configuration(source_file=path, restore_method=restore_method,
                                                 config_type=config_type, vrf=vrf)
        handler.logger.info('Restore completed')
        handler.logger.info(response)

    @context_from_args
    def save(self, context, destination_host, source_filename, vrf=None):
        """Save selected file to the provided destination

        :param source_filename: source file, which will be saved
        :param destination_host: destination path where file will be saved
        :param vrf: VRF management Name
        """

        handler = inject.instance('handler')
        response = handler.save_configuration(destination_host, source_filename, vrf)
        handler.logger.info('Save completed')
        return response

    @context_from_args
    def send_custom_command(self, context, command):
        """
        Send custom command
        :return: result
        :rtype: string
        """
        handler = inject.instance("handler")
        result_str = handler.send_command(command=command)
        return result_str

    @context_from_args
    def ApplyConnectivityChanges(self, context, request):
        handler = inject.instance('handler')
        responce = handler.apply_connectivity_changes(request)
        handler.logger.info('Finished applying connectivity changes responce is: {0}'.format(str(responce)))
        return responce

    @context_from_args
    def send_custom_config_command(self, context, command):
        handler = inject.instance("handler")
        result_str = handler.send_config_command(command=command)
        return result_str

    def shutdown(self, context):
        pass
