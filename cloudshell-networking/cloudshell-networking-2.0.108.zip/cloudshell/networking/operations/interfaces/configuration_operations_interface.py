from abc import ABCMeta
from abc import abstractmethod


class ConfigurationOperationsInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def save_configuration(self, destination_host, source_filename, vrf=None):
        pass

    @abstractmethod
    def restore_configuration(self, source_file, config_type, restore_method='override', vrf=None):
        pass
