import os
from os.path import abspath, dirname, join
import logging.config


PACKAGE = dirname(abspath(__file__))

LOGLEVEL = os.getenv('PY4JDBC_LOGLEVEL', 'INFO')
USE_COLOR = os.getenv('PY4JDBC_LOG_COLOR', 1) not in ('0', 'False')

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "%(asctime)s [%(name)s] %(levelname)s %(module)s::%(funcName)s: %(message)s",
            'datefmt': '%H:%M:%S'
        }
    },
    'handlers': {
        'default': {'level': 'INFO', 'formatter': 'standard',
                    'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'py4jdbc': {
            'handlers': ['default'], 'level': LOGLEVEL, 'propagate': True
        },
    },
}

if USE_COLOR:
    LOGGING_CONFIG['handlers']['default']['class'] = 'py4jdbc.ansiterm.ColorizingStreamHandler'

logging.config.dictConfig(LOGGING_CONFIG)
