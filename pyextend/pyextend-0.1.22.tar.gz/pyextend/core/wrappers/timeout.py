# coding: utf-8
"""
    pyextend.core.wrappers.timeout
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    pyextend core wrappers timeout wrapper

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""
import signal
import functools
from . import system as sys
from pyextend.core import log

# class TimeoutError(Exception): pass


def timeout(seconds, error_message=None):
    """Timeout checking just for Linux-like platform, not working in Windows platform."""
    def decorated(func):
        result = ""

        def _handle_timeout(signum, frame):
            errmsg = error_message or 'TimeoutError: The action <%s> is timeout!' % func.__name__
            log.warning(errmsg)
            log.warning("The action <%s> returns None value. check the None result before it using." % func.__name__)
            global result
            result = None
            raise TimeoutError(errmsg)

        @sys.platform(sys.UNIX_LIKE, case_false_wraps=func)
        def wrapper(*args, **kwargs):
            global result
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)

            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
                return result

        return functools.wraps(func)(wrapper)

    return decorated
