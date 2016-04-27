"""Resource Allocation API"""
import kvstore

PREFIX = 'resources'
DISK_PREFIX = 'disks'
ADDRESS_PREFIX = 'networks'


class ResourceManager(object):
    """Resource Management base class"""

    def __init__(self, endpoint='http://127.0.0.1:8500/v1/kv'):
        self.endpoint = endpoint
        self._kv = kvstore.Client(self.endpoint)

    def get_status(self, resource_status_path):
        """Returns the status of all the resources of a given node"""
        subtree = self._kv.recurse(
            '{}/{}'.format(PREFIX, resource_status_path))
        return {self._parse_res_name(k):
                subtree[k] for k in subtree.keys() if subtree[k] != ""}

    def set_status(self, resource_status_path, status):
        """Sets the status of a given resource"""
        self._kv.set(
            '{}/{}/status'.format(PREFIX, resource_status_path), status)

    def get_free(self, resource_status_path):
        """Returns the list of free resources of a given node"""
        subtree = self._kv.recurse('{}/{}'.format(PREFIX, resource_status_path))
        free_res = self._filter_res(subtree, status='free')
        return free_res

    def get_used(self, resource_status_path):
        """Returns the list of used resources of a given node"""
        subtree = self._kv.recurse('{}/{}'.format(PREFIX, resource_status_path))
        used_res = self._filter_res(subtree, status='used')
        return used_res

    def _parse_res_name(self, key):
        """Extract disk name from key"""
        return key.split('/')[-2]

    def _filter_res(self, subtree, status='free'):
        """Filter resources based on status"""
        if status == 'free':
            filtered_res = [self._parse_res_name(k)
                            for k in sorted(subtree.keys())
                            if subtree[k] == 'free']
        elif status == 'used':
            filtered_res = [self._parse_res_name(k)
                            for k in sorted(subtree.keys())
                            # Skip also the empty key (tree directory)
                            if subtree[k] != 'free' and subtree[k] != ""]
        else:
            raise StatusNotSupportedError()

        return filtered_res


class DiskManager(ResourceManager):
    """Manage disk allocations"""

    def get_used(self, node):
        return ResourceManager.get_used(self, DISK_PREFIX + "/" + node)

    def get_free(self, node):
        disks = ResourceManager.get_free(self, DISK_PREFIX + "/" + node)
        return {'number': len(disks), "disks": disks}

    def get_status(self, node, disk):
        return ResourceManager.get_status(self, DISK_PREFIX + "/" + node + "/" + disk)

    def set_status(self, node, disk, status):
        return ResourceManager.set_status(self, DISK_PREFIX + "/" + node + "/" + disk, status)

    def set_used(self, node, disk):
        return self.set_status(node, disk, "used")

    def set_free(self, node, disk):
        return self.set_status(node, disk, "free")


class AddressManager(ResourceManager):
    """Manage network address allocations"""

    def get_used(self, network):
        return ResourceManager.get_used(self, ADDRESS_PREFIX + "/" + network)

    def get_free(self, network):
        ips = ResourceManager.get_free(self, ADDRESS_PREFIX + "/" + network)
        return {'number': len(ips), "ips": ips}

    def get_status(self, network, ip):
        return ResourceManager.get_status(self, ADDRESS_PREFIX + network + "/" + ip)

    def set_status(self, network, ip, status):
        return ResourceManager.set_status(self, ADDRESS_PREFIX + network + "/" + ip, status)

    def set_used(self, network, ip):
        return self.set_status(network, ip, "used")

    def set_free(self, network, ip):
        return self.set_status(network, ip, "free")


class StatusNotSupportedError(Exception):
    pass
