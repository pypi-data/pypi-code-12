# -*- coding: utf-8 -*-
from datetime import datetime


def from_string(date_string, expected_formats=('%Y-%m-%d %H:%M:%S', '%Y-%m-%d')):
    for fmt in expected_formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            pass
    raise ValueError('Invalid date: {}'.format(date_string))


def dt_max(d, time=datetime.max.time()):
    return datetime.combine(d, time)


def dt_min(d, time=datetime.min.time()):
    return datetime.combine(d, time)
