# -*- coding: UTF-8 -*-
# lvjiyong on 2015/4/25.


def store(func):
    """
    存储信息到page
    :param func:
    :return:
    """
    def modify(*args, **kwargs):
        page = args[0]
        key = func.__name__
        value = page.stores.get(key)
        if not value:
            value = func(*args, **kwargs)
            if value:
                page.stores[key] = value
        return value
    return modify
