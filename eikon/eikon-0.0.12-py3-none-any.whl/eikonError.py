# coding: utf8


class EikonError(Exception):
    """Base class for exceptions in this module.

    :param value:
    :type value: a printable value
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
