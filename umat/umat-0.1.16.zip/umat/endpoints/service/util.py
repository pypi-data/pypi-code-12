# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta
)
from time import sleep
from six import reraise
from sys import exc_info


def print_bold(message, bold='\033[1m', default='\033[0m'):
    now = datetime.now().replace(microsecond=0).isoformat(' ')
    print('{} {}{}{}'.format(now, bold, message, default))


def retry(lives, delay=60):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            _lives = lives
            while _lives:
                _lives -= 1
                try:
                    result = fn(*args, **kwargs)
                except:
                    info = exc_info()
                    if _lives:
                        sleep(delay)
                    else:
                        reraise(*info)
                else:
                    return result
        return wrapper
    return decorator


def split_period(start_date, end_date, step=timedelta(hours=24*7), future=True):
    periods = []
    if not future:
        now = datetime.now()
        if end_date > now:
            end_date = now
    period_start_date = start_date
    while period_start_date < end_date:
        period_end_date = period_start_date + step
        if period_end_date > end_date:
            period_end_date = end_date
        if period_end_date > period_start_date:
            periods.append([period_start_date, period_end_date])
        period_start_date += step
    return periods
