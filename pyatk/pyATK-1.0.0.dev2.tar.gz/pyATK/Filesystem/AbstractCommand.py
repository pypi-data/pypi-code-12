# -*- coding: utf-8 -*-
from abc import ABCMeta


class AbstractCommand(metaclass=ABCMeta):
    def __init__(self):
        pass

    def execute(self):
        pass

    def undo(self):
        pass
