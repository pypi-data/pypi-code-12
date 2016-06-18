
from abc import ABCMeta, abstractmethod
from yapsy.IPlugin import IPlugin


class IModule(IPlugin):

    __metaclass__ = ABCMeta

    def __init__(self):
        self._name = "none"

    @property
    def name(self):
        """Set and Returns the Name of this Module"""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @abstractmethod
    def install(self, project):
        pass

