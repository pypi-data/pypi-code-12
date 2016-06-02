# -*- coding:utf-8 -*-

import time
import logging

TSLEEP = 10


def fail_counter(fn):
    def wrapped(self, *args, **kwargs):
        self.exceptions = 0
        while self.exceptions < 5:
            try:
                return fn(self, *args, **kwargs)
            except Exception as exc:
                logging.warning('DecoratorError: number of exceptions is %d' % self.exceptions)
                self.exceptions += 1
                time.sleep(TSLEEP)
        raise exc
    return wrapped
