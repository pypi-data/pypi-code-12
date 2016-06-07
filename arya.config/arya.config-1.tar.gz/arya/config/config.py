from attrdict import AttrDict
from xdg import BaseDirectory
import yaml
from yamlordereddictloader import Loader


def _module_args(module):
    args = module.split('.')
    args[-1] = '{}.yaml'.format(args[-1])
    return args


def _resource_args(resource, filename='config.yaml'):
    return resource, filename


class Config(AttrDict):
    def load(self, module=None, resource=None):
        self.clear()

        if module:
            args = _module_args(module)
        elif resource:
            args = _resource_args(resource)
        else:
            raise TypeError

        config_paths = reversed(list(BaseDirectory.load_config_paths(*args)))
        for filename in BaseDirectory.load_config_paths(*args):
            with open(filename) as f:
                obj = yaml.load(f, Loader=Loader)
                self.update(obj)
        return self


# hack
BaseDirectory.xdg_config_dirs.append('/etc')
