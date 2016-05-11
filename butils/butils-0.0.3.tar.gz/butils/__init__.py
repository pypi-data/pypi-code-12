import functools

import logging
logger = logging.getLogger()


def safe_method(f):
    """
    this method will not raise exception

    """

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.exception(e)

    return wrapper


class retry(object):
    """
    retry method on exception
    """
    def __init__(self, max_retries=3, exceptions=(Exception,)):
        self.max_retries = max_retries
        self.exceptions = exceptions

    def __call__(self, f, *args, **kwargs):
        def wrapper(*args, **kwargs):
            for i in range(self.max_retries + 1):
                try:
                    result = f(*args, **kwargs)
                except self.exceptions:
                    continue
                else:
                    return result
        return wrapper
