from abc import ABCMeta, abstractmethod


class BaseFileReader(metaclass=ABCMeta):

    @abstractmethod
    def read_file(self, filename):
        pass
