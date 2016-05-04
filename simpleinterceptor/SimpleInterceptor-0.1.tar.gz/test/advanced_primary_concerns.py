"""Interceptor testcase to intercept more than just methods"""


class PrimaryConcern(object):
    @classmethod
    def _class_method(cls, arg1):
        print "Class method", cls, arg1

    @staticmethod
    def _static_method(self, kwarg1='kwarg1'):
        print "Static method", self, kwarg1

    def _method(self, arg1, kwarg1=False):
        print "Normal method", self, arg1, kwarg1


class Celsius(object):
    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, val):
        self.value = float(val)


class Fahrenheit(object):
    def __get__(self, instance, owner):
        return instance.celsius * 9 / 5 + 32

    def __set__(self, instance, val):
        instance.celsius = (float(val) - 32) * 5 / 9


class DescTemperature(object):
    celsius = Celsius()
    fahrenheit = Fahrenheit()


class SigTemperature(object):
    def fget(self):
        return self.celsius * 9 / 5 + 32

    def fset(self, val):
        self.celsius = (float(val) - 32) * 5 / 9
    fahrenheit = property(fget, fset)

    def cget(self):
        return self.cval

    def cset(self, val):
        self.cval = float(val)
    celsius = property(cget, cset)


class DecTemperature(object):
    @property
    def fahrenheit(self):
        return self.celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, val):
        self.celsius = (float(val) - 32) * 5 / 9

    @property
    def celsius(self):
        return self.cval

    @celsius.setter
    def celsius(self, val):
        self.cval = float(val)
