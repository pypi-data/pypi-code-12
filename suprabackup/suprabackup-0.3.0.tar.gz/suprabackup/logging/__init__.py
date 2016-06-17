"""
This module handles suprabackup logging

"""

_DEFAULT_LOGGER_TAG = 'suprabackup'
_SYSLOG_SOCK = '/dev/log'


def get_logger(name=_DEFAULT_LOGGER_TAG):
    """
    Returns a logging instance for tag `name`

    """
    import logging

    return logging.getLogger(name)


def setup_logger(logger=None, verbose=False, debug=False, no_syslog=False, sock_path=_SYSLOG_SOCK):
    """
    Configure the logger with the given options
    if logger is None, it will be created using get_logger()

    The logger will be returned

    """
    import logging.handlers

    if not logger:
        logger = get_logger()
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    if verbose:
        logger.addHandler(logging.StreamHandler())
    if not no_syslog:
        try:
            handler = logging.handlers.SysLogHandler(sock_path)
            handler.setFormatter(logging.Formatter(
                    '%(asctime)s %(name)s: [%(levelname)s] %(message)s',
                    '%b %e %H:%M:%S'
                    ))
            logger.addHandler(handler)
        except Exception as e:
            logger.error("Cannot attach syslog handler to logging module: {0}"
                         .format(e.strerror))
    return logger


def setup_logging(name=_DEFAULT_LOGGER_TAG, verbose=False, debug=False, no_syslog=False):
    """
    Does the same as setup_logger instead it calls get_logger() with `name`

    """
    return setup_logger(get_logger(name), verbose=verbose, debug=debug, no_syslog=no_syslog)
