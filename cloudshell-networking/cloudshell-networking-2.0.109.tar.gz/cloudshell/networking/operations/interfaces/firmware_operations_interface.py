from abc import ABCMeta
from abc import abstractmethod


class FirmwareOperationsInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def update_firmware(self, remote_host, file_path, size_of_firmware):
        pass
