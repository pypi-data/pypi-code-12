import logging
from .base_client import BaseF5Client


log = logging.getLogger(__name__)


class F5Client(BaseF5Client):

    def set_self_ip(self, payload):
        return self._set_self_ip(payload)

    def set_vlan(self, payload):
        return self._set_vlan(payload)

    def get_net_self(self):
        return self._get_net_self()

    def set_gtm_wideip_pools(self, name, pools, partition='Common'):
        """Sets the GTM Wide IP Pool for a particular entry

        Args:
            name (str): Name of the wide ip to set
            pools (list[str]): A list of pools to set for the wide ip
            partition (str): The partition of the wide ip. (Default: Common)

        Returns:
            bool: True if success
        """
        if not isinstance(pools, (list, tuple)):
            raise TypeError("pools must be a list or tuple")
        payload = {}
        payload['pools'] = []
        for pool in pools:
            pool_dict = {'name': pool}
            payload['pools'].append(pool_dict)

        return self.set_gtm_wideip(name, payload, partition)

    def set_gtm_wideip(self, name, payload, partition='Common'):
        """Sets the GTM Wide IP for a particular entry

        Args:
            name (str): Name of the wide ip to set
            payload (str): The payload to send to the wide ip entry
            partition (str): The partition of the wide ip. (Default: Common)

        Returns:
            bool: True if success
        """
        return self._set_gtm_wideip(name, partition, payload)

    def get_gtm_wideip_pools(self, name, partition='Common'):
        """Gets the pools for a particular GTM Wide IP entry

        Args:
            name (str): Name of the wide ip to set
            partition (str): The partition of the wide ip. (Default: Common)

        Returns:
            list[str]: List of pool names associated with the wide ip entry
        """
        gtm_info = self.get_gtm_wideip_config(name, partition)
        return [pool['name'] for pool in gtm_info['pools']]

    def get_gtm_wideip_config(self, name, partition='Common'):
        """Gets the config for a particular GTM Wide IP entry

        Args:
            name (str): Name of the wide ip to set
            partition (str): The partition of the wide ip. (Default: Common)

        Returns:
            dict: Full configuration of the wide ip entry
        """
        return self._get_gtm_wideip(name, partition)
