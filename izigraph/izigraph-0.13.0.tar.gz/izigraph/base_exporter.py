from abc import ABCMeta, abstractmethod


class BaseExporter:
    __metaclass__ = ABCMeta

    @abstractmethod
    def export(self, graph, routes=None):
        raise NotImplementedError
