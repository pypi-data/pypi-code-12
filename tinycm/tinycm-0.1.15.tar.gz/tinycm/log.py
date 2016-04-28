import logging
import colorlog
import sys


def setup_logger(name, level):

    format = '{log_color}{levelname:8}{message}'

    formatter = colorlog.ColoredFormatter(format, style='{')
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger