# encoding: utf-8
import time
from typing import Callable

__author__ = 'yonka'


def schedule_task(fn, initial_delay: float=0, period: float=0, repeat=1) -> Callable:
    """
    @:param fn should handle exception itself
    @:param repeat <= 0 means infinite repeat
    """

    def _fn(*args, **kwargs):
        cnt = 0
        if initial_delay > 0:
            time.sleep(initial_delay)
        while repeat <= 0 or repeat > cnt:
            cnt += 1
            fn(*args, **kwargs)
            if period > 0:
                time.sleep(period)

    return _fn


def timestamp():
    return int(time.time() * 1000)
