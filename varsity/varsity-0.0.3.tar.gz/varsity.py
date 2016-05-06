import os

from attrdict import AttrDict

__version__ = '0.0.3'


class Loader():
    def __init__(self):
        self._settings = []

    def add(self, name=None, var=None, default=None, typ=None):
        assert name, 'You must provide a setting name'
        assert var, 'You must provide an environment variable name'
        if typ is None and default is not None:
            typ = type(default)
        self._settings.append((name, var, default, typ))

    def load(self, environ=None):
        if environ is None:
            environ = os.environ
        return AttrDict({
            name: self.load_value(environ, var, default, typ)
            for name, var, default, typ in self._settings
        })

    def load_value(self, environ, var, default, typ):
        value = environ.get(var)
        if value is None:
            if default is not None:
                return default
            raise ValueError('%s environment variable not set, and '
                             'no default provided.' % var)
        if typ:
            value = typ(value)
        return value
