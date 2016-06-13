from cloudshell.networking.cisco.cisco_configuration_operations import CiscoConfigurationOperations
import re


class CiscoNXOSConfigurationOperations(CiscoConfigurationOperations):
    def __init__(self):
        CiscoConfigurationOperations.__init__(self)

    def _check_replace_command(self):
        return True

    def configure_replace(self, source_filename, timeout=600, vrf=None):
        if not source_filename:
            raise Exception('Cisco NXOS', 'Must pass source file name to replace configuration')
        back_up = 'bootflash:backup-sc'
        startup = 'startup-config'

        self._backup_startup_config(back_up, startup, vrf)
        self._replace_startup_config_with(source_filename, vrf)
        self._logger.info('Reload device after applying configuration ...')
        self.reload(retries=19, sleep_timeout=30)
        self._replace_startup_config_with(back_up, vrf)

    def _backup_startup_config(self, back_up, startup, vrf):
        if not self.copy(source_file=startup, destination_file=back_up, vrf=vrf):
            raise Exception('Cisco NXOS', 'Could not backup startup-config, check if bootflash has enough free space')

    def _replace_startup_config_with(self, source_filename, vrf):
        # its not possible to copy directly from TFTP to startup, so first copy to local, then from local to start
        sc = 'startup-config'
        lc = 'bootflash:local-copy'
        self.copy(source_file=source_filename, destination_file=lc)
        if not self.copy(source_file=lc, destination_file=sc, vrf=vrf):
            raise Exception('Cisco NXOS', 'Failed to replace startup config, detailed information in logs')

