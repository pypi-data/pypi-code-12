import os

from attrdict import AttrDict

__version__ = '0.0.5'


class Loader():
    def __init__(self):
        self._settings = []

    def add(self, var, name=None, default=None, typ=None, required=True):
        if not isinstance(var, str):
            raise ValueError('Environment variable %s is not a string' % var)
        if name is None:
            name = var

        if typ is None and default is not None:
            typ = type(default)
            if typ == bool:
                typ = nice_bool
        self._settings.append((name, var, default, typ, required))

    def load(self, environ=None):
        if environ is None:
            environ = os.environ
        return AttrDict({
            name: self.load_value(environ, var, default, typ, required)
            for name, var, default, typ, required in self._settings
        })

    def load_value(self, environ, var, default, typ, required):
        value = environ.get(var)
        if value is None:
            if default is not None:
                return default
            if required is False:
                return None
            raise ValueError('%s environment variable not set, and '
                             'no default provided.' % var)
        if typ:
            value = typ(value)
        return value


def nice_bool(val):
    if val.lower() in {'yes', 'true', '1'}:
        return True
    if val.lower() in {'no', 'false', '0'}:
        return False
    raise ValueError("Cannot parse %s into a bool" % val)
