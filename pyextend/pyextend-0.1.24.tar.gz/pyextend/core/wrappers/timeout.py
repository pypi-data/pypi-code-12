# coding: utf-8
"""
    pyextend.core.wrappers.timeout
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    pyextend core wrappers timeout wrapper

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""
import os
import sys
import signal
import functools
from . import system as sysx


if sysx.version_info < (3,):
    class TimeoutError(OSError):
        """ Timeout expired. """

        def __init__(self, *args, **kwargs):  # real signature unknown
            pass


def timeout(seconds, error_message=None):
    """Timeout checking just for Linux-like platform, not working in Windows platform."""

    def decorated(func):
        result = ""

        def _handle_timeout(signum, frame):
            errmsg = error_message or 'Timeout: The action <%s> is timeout!' % func.__name__
            global result
            result = None
            import inspect
            stack_frame = inspect.stack()[4]
            file_name = os.path.basename(stack_frame[1])
            line_no = stack_frame[2]
            method_name = stack_frame[3]
            code_text = ','.join(stack_frame[4])
            stack_info = 'Stack: %s, %s:%s >%s' % (method_name, file_name, line_no, code_text)
            sys.stderr.write(errmsg+'\n')
            sys.stderr.write(stack_info+'\n')
            raise TimeoutError(errmsg)

        @sysx.platform(sysx.UNIX_LIKE, case_false_wraps=func)
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
