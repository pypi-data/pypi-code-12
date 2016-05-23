# -*- coding: utf-8 -*-

import sys
import inspect

import re

from robot.libraries import BuiltIn
BUILTIN = BuiltIn.BuiltIn()

try:
    from decorator import decorator
except SyntaxError:  # decorator module requires Python/Jython 2.4+
    decorator = None
if sys.platform == 'cli':
    decorator = None  # decorator module doesn't work with IronPython 2.6


def _run_on_failure_decorator(method, *args, **kwargs):
    try:
        if(re.search(r'[Cc]lick|[Ii]nput',method.__name__)):
            self = args[0]
            self.capture_page_screenshot_without_html_log()
        return method(*args, **kwargs)
    except Exception, err:
        self = args[0]
        if hasattr(self, '_run_on_failure'):
            self._run_on_failure()
        raise


class KeywordGroupMetaClass(type):
    def __new__(cls, clsname, bases, dict):
        if decorator:
            for name, method in dict.items():
                if not name.startswith('_') and inspect.isroutine(method):
                    dict[name] = decorator(_run_on_failure_decorator, method)
        return type.__new__(cls, clsname, bases, dict)


class KeywordGroup(object):
    __metaclass__ = KeywordGroupMetaClass
