import os
from yaml import load


CONFIG_DIRECTORY = os.path.expanduser('~/.maintain')


class Config(object):
    @classmethod
    def path_for_config(cls, name):
        return os.path.join(CONFIG_DIRECTORY, name + '.yaml')

    @classmethod
    def gather(cls, names):
        if not os.path.exists(CONFIG_DIRECTORY):
            os.makedirs(CONFIG_DIRECTORY)

        return cls.load_config('default', cls.path_for_config('default'))

    @classmethod
    def load_config(cls, name, path):
        with open(path) as fp:
            settings = load(fp)

        return cls(name=name, path=path, settings=settings)

    def __init__(self, settings={}, name=None, path=None):
        self.name = name
        self.path = path
        self.settings = settings

    def __getitem__(self, key):
        keys = key.split('.')
        current = self.settings

        for key in keys:
            if current == False or current == None:
                return current

            try:
                current = current[key]
            except (TypeError, AttributeError, KeyError):
                return None

        return current

    def __contains__(self, key):
        return key in self.settings

    def keys(self):
        return self.settings.keys()

    def get(self, *args, **kwargs):
        return self.settings.get(*args, **kwargs)

