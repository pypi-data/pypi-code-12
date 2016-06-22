import logging

import docido_sdk.config as app_config


def set_root_logger_from_verbosity(verbosity=0):
    """Configure root logger according to both application settings
    and verbosity level.
    """
    level = logging.WARN
    if verbosity == 1:
        level = logging.INFO
    elif verbosity > 1:
        level = logging.DEBUG
    set_root_logger(level=level)


def set_root_logger(config=None, **kwargs):
    """
    :param dict config:
      Override application global settings.

    :param dict kwargs:
      Additional arguments given to :py:method:`logging.basicConfig`
    """
    config = config or app_config
    logging_config = config.get('logging') or {}
    kwargs.setdefault('level', logging_config.get('level'))
    kwargs.setdefault('format', logging_config.get('format'))
    logging.basicConfig(**kwargs)


def set_loggers_from_config(config=None):
    """Set loggers configuration according to the `logging` section
    of Docido configuration file.

    :param nameddict config:
      overrides Docido configuration
    """
    config = config or app_config.logging
    for lname, lconfig in config.get('loggers', {}).iteritems():
        if 'level' in lconfig:
            level = getattr(logging, lconfig.level)
            assert isinstance(level, int)
            logger = logging.getLogger(lname)
            logger.setLevel(level)
