from ubackup import settings

import logging
import os

# Import correct dictConfig depending on the Python version
try:
    from logging.config import dictConfig
except ImportError:
    from logutils.dictconfig import dictConfig


def level_names():
    levels = logging._levelNames.items()
    levels = map(lambda (k, v): v if isinstance(k, int) else None, levels)
    return filter(None, levels)


def set_level(level_name):
    # logging.getLogger().setLevel(level_name)
    for handler in logging.getLogger().handlers:
        handler.setLevel(level_name)


def set_config(config):
    # Add a RotatingFileHandler to logging config
    if not os.path.exists(settings.LOG_DIRECTORY):
        try:
            os.mkdir(settings.LOG_DIRECTORY)
        except OSError:
            pass
    if os.path.exists(settings.LOG_DIRECTORY):
        config['handlers']['rotate_file'] = {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': os.path.join(settings.LOG_DIRECTORY, 'ubackup.log'),
            'backupCount': 5,
            'maxBytes': 1024 * 1024 * 20
        }
        for logger, obj in config['loggers'].items():
            obj['handlers'].append('rotate_file')

    dictConfig(config)
