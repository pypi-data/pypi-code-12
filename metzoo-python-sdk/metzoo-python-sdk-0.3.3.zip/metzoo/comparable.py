# -*- coding: utf-8 -*-

class Comparable(object):
    def __eq__(self, other):
        if type(self) is type(other):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        return not self.__ne__(other)
