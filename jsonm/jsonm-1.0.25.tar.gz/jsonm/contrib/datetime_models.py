# -*- coding: utf-8 -*-

"""
datetime.datetime, datetime.date 的models
"""

import datetime


def datetime_to_json(python_object):
    fmt = '%Y-%m-%d %H:%M:%S.%f'
    return dict(
        __class__=python_object.__class__.__name__,
        __value__=python_object.strftime(fmt),
    )


def datetime_from_json(json_object):
    json_value = json_object['__value__']
    fmt = '%Y-%m-%d %H:%M:%S.%f'
    return datetime.datetime.strptime(json_value, fmt)


def date_to_json(python_object):
    fmt = '%Y-%m-%d'
    return dict(
        __class__=python_object.__class__.__name__,
        __value__=python_object.strftime(fmt),
    )


def date_from_json(json_object):
    json_value = json_object['__value__']
    fmt = '%Y-%m-%d'
    return datetime.datetime.strptime(json_value, fmt).date()


DATETIME_MODELS = (
    dict(
        type=datetime.datetime,
        to_json=datetime_to_json,
        from_json=datetime_from_json,
    ), dict(
        type=datetime.date,
        to_json=date_to_json,
        from_json=date_from_json,
    )
)
