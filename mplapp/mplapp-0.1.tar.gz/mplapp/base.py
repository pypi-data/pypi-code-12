from abc import ABCMeta, abstractmethod


class Base(object):


    __metaclass__ = ABCMeta


    @abstractmethod
    def _render(self, fig, x, y):
        pass


    @abstractmethod
    def axes(self):
        pass


    @abstractmethod
    def canvas(self):
        pass


    @abstractmethod
    def size(self):
        pass

