from abc import ABCMeta, abstractmethod


class BaseImporter:
    __metaclass__ = ABCMeta

    @abstractmethod
    def import_graph(self, to_import):
        raise NotImplementedError
