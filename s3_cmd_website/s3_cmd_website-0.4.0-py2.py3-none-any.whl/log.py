import logging
import exitcodes


ROOT_LOGGER_NAME = 'root'


def setup_logger(log_level):
    """
    Common function for setting up a logger

    :param log_level: string - The log level as a string to be used
    """
    formatter = logging.Formatter(
        fmt='%(asctime)s: %(processName)s: %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(ROOT_LOGGER_NAME)

    numeric_level = getattr(logging, log_level.upper(), None)

    if not isinstance(numeric_level, int):
        print "Invalid log level: '%s'" % log_level
        exit(exitcodes.EX_ERROR)

    logger.setLevel(numeric_level)
    logger.addHandler(handler)
    return logger
