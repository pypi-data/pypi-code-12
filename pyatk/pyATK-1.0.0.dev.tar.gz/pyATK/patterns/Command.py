
from abc import ABC, abstractmethod


class AbstractCommand(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass
