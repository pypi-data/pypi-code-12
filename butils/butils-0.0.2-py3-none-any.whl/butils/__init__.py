import functools

import logging
logger = logging.getLogger()


def safe_method(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.exception(e)

    return wrapper
