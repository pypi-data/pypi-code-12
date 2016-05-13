from types import *
class trilean:
    def __init__ (self, x, y=None, embedded=None):
        if type(x) is IntType:
            if x <= 2:
                self.value = x
                self.table = Trilean.createTable(x)
                self.embedded = y
            else:
                raise ValueError("Error: Invalid argument at poisition 0")
        elif type(x) is BooleanType:
            if type(y) is BooleanType:
                v = Trilean.Parse(x, y).value
                self.value = v
                self.table = Trilean.createTable(v)
                self.embedded = embedded
            else:
                v = Trilean.Parse(x).value
                self.value = v
                self.table = Trilean.createTable(v)
                self.embedded = y
        elif type(x) is StringType:
            self.value = Trilean.Parse(x).value
            self.table = Trilean.createTable(self.value)
            self.embedded = y
        else:
            raise ValueError("Invalid argument type. For (x, y, embedded), x must either be a number, boolean, or a string; y must be a boolean or null; and embedded must be any object or null")

class Trilean:
    @staticmethod
    def Parse (x, y = False):
        if type(x) is BooleanType:
            if y is True:
                return trilean(1)
            elif x is True:
                return trilean(0)
            else:
                return trilean(2)
        elif type(x) is StringType:
            if x is "true" or x is "0":
                return trilean(0)
            elif x is "middle" or x is "1":
                return trilean(1)
            elif x is false or x is "2":
                return trilean(2)
            else:
                raise ValueError("Error: Invalid String. Must be either \"true\", \"middle\", or \"false\"")
    @staticmethod
    def createTable(x):
        if type(x) is IntType:
            if x is 0:
                return [True, False]
            elif x is 1:
                return [False, True]
            elif x is 2:
                return [False, False]
            else:
                raise ValueError("Error: Invalid argument at position 0")
        else:
            raise ValueError("Error: Invalid argument at position 0")