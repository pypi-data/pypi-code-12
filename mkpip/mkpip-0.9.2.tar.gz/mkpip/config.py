'''
mkpip.config
'''
import os
from confutil import Config

CONFIG = Config('mkpip').__data__
CONFIGS = {}
DEFAULT = CONFIG.get('default', {})

for name, data in CONFIG.items():
    if not isinstance(data, dict):
        DEFAULT[name] = data
    if name == 'default':
        DEFAULT.update(data)

for name, data in CONFIG.items():
    if not isinstance(data, dict):
        continue
    if name == 'default':
        continue
    new = DEFAULT.copy()
    new.update(data)
    CONFIGS[name] = new

CONFIGS['default'] = DEFAULT


def config_getter(config_name='default', args={}):
    '''
    Gets a value for a config in order of:
     - command line args
     - environment variables
     - configuration in ~/.mkpip.cfg
     - default value passed.
    '''
    if config_name not in CONFIGS:
        print('[{0}] isn\'t present in ~/.mkpip.cfg, please setup your '
              'config.'.format(config_name))
    config = CONFIGS.get(config_name, {})

    def get(key, default=None):
        if args.get(key):
            return args[key]
        if os.getenv(key):
            return os.getenv(key)
        if config.get(key):
            return config[key]
        return default
    return get
