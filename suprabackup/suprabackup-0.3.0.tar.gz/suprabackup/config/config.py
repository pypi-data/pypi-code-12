"""
This module contains the base class to deal with configuration

"""

class SupraConfig(dict):
    """
    This class stores the configuration for suprabackup
    It is a simple dict with few helpers

    """
    def __init__(self):
        self.file = None

    @classmethod
    def from_file(klass, path, defaults=None):
        """
        Loads the configuration from file (use defaults if provided)
        The options in the config files will override the defaults

        Returns an instance of SupraConfig

        """
        import yaml

        c = klass()
        if defaults:
            c.update(defaults)
        with open(path) as f:
            config = yaml.safe_load(f)
            if config is None:
                config = {}
            c.update(config)
        c.file = path
        return c
