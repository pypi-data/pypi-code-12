from abc import ABCMeta, abstractmethod


class BaseDataCollector(metaclass=ABCMeta):

    @abstractmethod
    def collect_data(self, source):
        pass
