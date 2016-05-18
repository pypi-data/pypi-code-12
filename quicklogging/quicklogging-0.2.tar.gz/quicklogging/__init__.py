"""
Module quicklogging
=======================

(logging with a bit of cozyness)

log wrappers
-------------

    Supplied convenience functions fetch a logger with the name
    of the module from which you're calling them.

.. autofunction:: debug

.. autofunction:: info

.. autofunction:: warning

.. autofunction:: error

.. autofunction:: critical

.. autofunction:: exception

print handlers
---------------

.. autofunction:: catch_prints

.. autofunction:: warn_prints

"""

import sys

from .base import _log_with_level
from .base import get_logger
from .stream_wrapper import StreamWrapper


def debug(*args, **kwargs):
    """wrapper for :py:meth:`logging.Logger.debug`

    Variadic parameters: see :py:meth:`logging.Logger.debug`

    :param int stackoverhead: see :py:func:`quicklogging.base.get_logger`
    """
    stackoverhead = kwargs.pop('stackoverhead', 1)
    _log_with_level('debug', stackoverhead=stackoverhead, *args, **kwargs)


def info(*args, **kwargs):
    """wrapper for :py:meth:`logging.Logger.info`

    Variadic parameters: see :py:meth:`logging.Logger.info`

    :param int stackoverhead: see :py:func:`quicklogging.base.get_logger`
    """
    stackoverhead = kwargs.pop('stackoverhead', 1)
    _log_with_level('info', stackoverhead=stackoverhead, *args, **kwargs)


def warning(*args, **kwargs):
    """wrapper for :py:meth:`logging.Logger.warning`

    Variadic parameters: see :py:meth:`logging.Logger.warning`

    :param int stackoverhead: see :py:func:`quicklogging.base.get_logger`
    """
    stackoverhead = kwargs.pop('stackoverhead', 1)
    _log_with_level('warning', stackoverhead=stackoverhead, *args, **kwargs)


def error(*args, **kwargs):
    """wrapper for :py:meth:`logging.Logger.error`

    Variadic parameters: see :py:meth:`logging.Logger.error`

    :param int stackoverhead: see :py:func:`quicklogging.base.get_logger`
    """
    stackoverhead = kwargs.pop('stackoverhead', 1)
    _log_with_level('error', stackoverhead=stackoverhead, *args, **kwargs)


def critical(*args, **kwargs):
    """wrapper for :py:meth:`logging.Logger.critical`

    Variadic parameters: see :py:meth:`logging.Logger.critical`

    :param int stackoverhead: see :py:func:`quicklogging.base.get_logger`
    """
    stackoverhead = kwargs.pop('stackoverhead', 1)
    _log_with_level('critical', stackoverhead=stackoverhead, *args, **kwargs)


def exception(*args, **kwargs):
    """wrapper for :py:meth:`logging.Logger.exception`

    Variadic parameters: see :py:meth:`logging.Logger.exception`

    :param int stackoverhead: see :py:func:`quicklogging.base.get_logger`
    """
    stackoverhead = kwargs.pop('stackoverhead', 1)
    _log_with_level('exception', stackoverhead=stackoverhead, *args, **kwargs)


_CUR_MODULE = object()


def warn_prints(catch_all=False):
    """Activate warning when print is called

    :param bool catch_all: defaults to False, ie. defaults to only warn about
        current module, ignoring imports"""
    raise NotImplementedError("API is yet to be defined, please help me.")


def catch_prints(
    catch_module=_CUR_MODULE,
    catch_all=False,
    include_children=True,
    logfunc=info,
):
    """configure the print() catching: redirects calls to a logger

    By default, only catches calls to print() from logger

    * named after the calling module
    * children of this logger


    .. note::

        API discussion welcome.

        You anderstand the API is not stable.

    :param string catch_module: include children of logger designed by name
    :param bool catch_all: should catch all print() diregarding where
        they're from ?

        .. warning::

            take care of logging propagation (``Logger.propagate()̀``)

    :param function logfunc: function to use for logging messages

    Possible extension ideas:

        * wrap arbitrary output stream
        * different log functions depending on regex applied on messages
        * make it configurable from config file
        * allow exclusion of specific modules
    """
    wrapper, created = StreamWrapper.get_wrapper(
        'sys.stdout',
        sys.stdout,
        logfunc,
        catch_all=catch_all,
    )
    if created:
        sys.stdout = wrapper

    if catch_module is _CUR_MODULE:
        catch_module = get_logger(stackoverhead=1).name

    wrapper.include_in_catch(catch_module, include_children)
