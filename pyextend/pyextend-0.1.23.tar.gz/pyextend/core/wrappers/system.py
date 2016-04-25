# coding: utf-8
"""
    pyextend.core.wrappers.system
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    pyextend core wrappers platform wrapper

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""
import platform as sys_platform
import functools

__all__ = ['LINUX', 'WINDOWS', 'MAC', 'UNIX_LIKE', 'platform']

LINUX = 'Linux'
WINDOWS = 'Windows'
MAC = 'Darwin'
UNIX_LIKE = [LINUX, MAC]


def platform(platform_name, case_true_wraps=None, case_false_wraps=None, case_false_result=None):
    def decorated(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if sys_platform.system() in platform_name:
                return functools.wraps(func)(case_true_wraps)(*args, **kwargs) if case_true_wraps \
                    else func(*args, **kwargs)
            else:
                return functools.wraps(func)(case_false_wraps)(*args, **kwargs) if case_false_wraps \
                    else case_false_result
        return wrapper
    return decorated
