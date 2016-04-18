import os


class Environment(object):
    environ = os.environ

    def __init__(self, **kwargs):
        for key, config in kwargs.items():
            validator, default = config
            value = self.environ.get(key, default)
            value = validator(value)
            setattr(self, key, value)
