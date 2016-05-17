#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

########################################################################
# Context
########################################################################
class Context(metaclass=ABCMeta):

    @abstractmethod
    def input(self, name):
        pass

    @abstractmethod
    def output(self, value):
        pass