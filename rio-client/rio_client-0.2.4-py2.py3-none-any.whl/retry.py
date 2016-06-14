# -*- coding: utf-8 -*-
"""
rio.retry
~~~~~~~~~
"""

import time
from functools import wraps


class RetryExceededError(Exception):
    """Throw when error retry too many times."""


class Retry(object):
    '''A decorator encapsulated retry logic.
    Usage:
    @retry(errors=(TTransportException, AnyExpectedError))
    @retry() # detect whatsoever errors and retry 3 times
    '''

    def __init__(self, errors=(Exception, ), tries=3, delay=0):
        self.errors = errors
        self.tries = tries
        self.delay = delay

    def __call__(self, func):
        @wraps(func)
        def _(*args, **kw):
            """Retry function"""
            retry_left_count = self.tries
            while retry_left_count:
                try:
                    return func(*args, **kw)
                except Exception as e: # pylint: disable=W0703
                    retry_left_count -= 1

                    if not isinstance(e, self.errors):
                        raise e

                    if not retry_left_count:
                        raise RetryExceededError

                    if self.delay:
                        time.sleep(self.delay)
        return _
