import imp
import logging
import os

DEFAULT_CONFIG_FILENAMES = [
    '/etc/mysql-corsair-settings.py', '~/.mysql-corsair'
]
logger = logging.getLogger(__name__)


def get_logging_config(log_level="INFO"):
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': log_level,
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': log_level,
                'propagate': False
            }
        }
    }


def load_config(config_file_path=None):
    """
    Load configuration.
    """
    config = None
    if config_file_path:
        config_file_path = os.path.expanduser(config_file_path)
        if not os.path.exists(config_file_path):
            raise IOError("Can't locate a configuration file at {0}".format(
                config_file_path
            ))
        config = imp.load_source('MySQLCorsair.settings', config_file_path)
        logging.debug('Loading configuration from {0}'.format(
            config_file_path)
        )

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
        raise ImportError("No configuration was found for MySQLCorsair.")

    return config
