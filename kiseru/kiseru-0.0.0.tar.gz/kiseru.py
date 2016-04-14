from functools import wraps


class ArgumentError(Exception):
    pass


class Kiseru(object):
    def __init__(self, cmd):
        if not callable(cmd):
            raise ArgumentError('argument must be callable object.')
        self.cmd = cmd

    def __ror__(self, other):
        return self.cmd(other)

    def __call__(self, *args, **kwargs):
        return self.cmd(*args, **kwargs)


def kiseru(func):
    return Kiseru(func)
