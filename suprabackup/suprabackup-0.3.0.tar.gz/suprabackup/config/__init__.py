"""
This package handles suprabackup config options loading

"""
from .config import SupraConfig

DEFAULT_CONFIG_PATH = '/etc/suprabackup/config.yml'


def load_config(role=None, overrides=None, path=DEFAULT_CONFIG_PATH):
    """
    Loads the configuration from a config file using the defaults as fallback
    `overrides allows to override some config options`

    """
    from .defaults import load_defaults

    defaults = load_defaults(role)
    config = SupraConfig.from_file(path, defaults)
    if overrides:
        config.update(overrides)
    return config
