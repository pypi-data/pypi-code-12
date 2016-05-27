import imp
import os

DEFAULT_CONFIG_FILENAMES = [
    '/etc/mysql-corsair-settings.py', '~/.mysql-corsair'
]


def load_config(self, config_file_path=None):
    """
    Load configuration.
    """
    config = None
    if config_file_path:
        config = imp.load_source('MySQLCorsair.settings', config_file_path)
    else:
        for filename in DEFAULT_CONFIG_FILENAMES:
            try:
                with open(os.path.expanduser(filename), "rb") as f:
                    config = imp.load_source('MySQLCorsair.settings',
                                             f.name)
            except (ImportError, IOError):
                # Move on to the next potential config file name.
                continue
    if not config:
        raise Exception("No configuration was found for MySQLCorsair.")

    return config
