# coding: utf-8
"""
    pyextend.core.wrappers.singleton
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    pyextend core wrappers singleton wrapper

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""


def singleton(cls, *args, **kwargs):
    """类单例装饰器"""
    instance = {}

    def _singleton():
        if cls not in instance:
            instance[cls] = cls(*args, **kwargs)
        return instance[cls]
    return _singleton
