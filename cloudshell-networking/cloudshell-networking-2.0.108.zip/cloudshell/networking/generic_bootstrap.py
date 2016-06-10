from cloudshell.shell.core.driver_bootstrap import DriverBootstrap

class NetworkingGenericBootstrap(DriverBootstrap):

    def bindings(self, binder):
        """Default bindings for all required handlers:
        1. Connectivity Operations handler
        2. Send Command handler
        3. Configuration Operations handler
        4. Firmware Operation handler
        """

        """Binding for connectivity operations handler"""
        binder.bind_to_provider('connectivity_operations', self._config.CONNECTIVITY_OPERATIONS_CLASS)

        """Binding for configuration operations handler"""
        binder.bind_to_provider('configuration_operations', self._config.CONFIGURATION_OPERATIONS_CLASS)

        """Binding for firmware operations handler"""
        binder.bind_to_provider('firmware_operations', self._config.FIRMWARE_OPERATIONS_CLASS)

        """Binding for firmware operations handler"""
        binder.bind_to_provider('autoload_operations', self._config.AUTOLOAD_OPERATIONS_CLASS)

        """Binding for send command operations handler"""
        binder.bind_to_provider('send_command_operations', self._config.SEND_COMMAND_OPERATIONS_CLASS)
