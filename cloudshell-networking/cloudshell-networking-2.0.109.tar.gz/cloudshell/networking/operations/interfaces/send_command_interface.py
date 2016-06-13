from abc import ABCMeta
from abc import abstractmethod


class SendCommandInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def send_command(self, command):
        pass

    @abstractmethod
    def send_config_command(self, command):
        pass
