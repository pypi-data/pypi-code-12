import logging.config

from oct_turrets.config import LOGGING_CONFIG

__version__ = '0.2.5'


logging.config.dictConfig(LOGGING_CONFIG)
