from abc import ABCMeta, abstractmethod
from yapsy.IPlugin import IPlugin


class ICommand(IPlugin):

    __metaclass__ = ABCMeta

    @abstractmethod
    def run(self, project):
        pass

    @abstractmethod
    def build(self, subparser):
        pass
