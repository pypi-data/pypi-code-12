__author__ = 'CoYe'

import re

from cloudshell.snmp.quali_snmp import QualiSnmp
from cloudshell.core.logger import qs_logger

class HardwarePlatformDetector:
    RESOURCE_DRIVERS_MAP = {}

    def __init__(self, ip, user='', password='', community='',  private_key='', version='2', logger=None):
        self.snmp = None
        self._logger = logger if logger else qs_logger.get_qs_logger(handler_name='SNMP_Hardware_Detector')
        #ToDo ask Gal do we really support v1 snmp, according to the fact it has restrictions for loading mib(unclarified)
        if version == '':
            self._logger.info('"SNMP Version" parameter is empty. Use snmp v2 as default.')
            version = '2'
        if '3' in version:
            self.init_snmp_v3(ip, user, password, private_key)
        else:
            self.init_snmp_v2(ip, community)
        self._test_snmp_agent()
        self._logger.info('Snmp handler created. Version {0}'.format(version))

    def init_snmp_v2(self, ip, community):
        """
        Create snmp handler version 2 or 1
        """
        self._logger.info("Initiate SNMP v2 with IP: {0}, Communiti: {1}".format(ip, community))
        if community == '':
            self._logger.error('"SNMP Read Community" parameter is empty!')
            raise Exception('"SNMP Read Community" parameter is empty!')
        self.snmp = QualiSnmp(ip=ip, community=community, logger=self._logger)

    def init_snmp_v3(self, ip, user, password, private_key):
        """
        Create snmp handler version 3
        """
        if user == '':
            self._logger.error('"SNMP V3 User" parameter is empty')
            raise Exception('"SNMP V3 User" parameter is empty')
        if password == '':
            self._logger.error('"SNMP V3 Password" parameter is empty')
            raise Exception('"SNMP V3 Password" parameter is empty')
        if private_key == '':
            self._logger.error('"SNMP V3 Private Key" parameter is empty')
            raise Exception('"SNMP V3 Private Key" parameter is empty')
        v3_user = {'userName': user, 'authKey': password, 'privKey': private_key}
        self.snmp = QualiSnmp(ip=ip, v3_user=v3_user)

    def _test_snmp_agent(self):
        """
        Validate snmp agent and connectivity attributes, raise Exception if snmp agent is invalid
        """
        try:
            self.snmp.get(('SNMPv2-MIB', 'sysName', '0'))
        except Exception as e:
            self._logger.error('Snmp agent validation failed')
            self._logger.error(e.message)
            raise Exception('Snmp attributes or host IP is not valid\n{0}'.format(e.message))

    def _detect_hardware_platform(self):
        """
        Detect target device platform
        :return: handler name
        :rtype: string
        """
        handler = None
        hardware_info = self.snmp.get(('SNMPv2-MIB', 'sysObjectID', '0')).values()[0]
        device_id = hardware_info.split('.')[-1]
        if device_id in self.RESOURCE_DRIVERS_MAP:
            handler = self.RESOURCE_DRIVERS_MAP[device_id]
        if handler:
            self._logger.info('Detected platform: {0}'.format(handler))
        return handler