"""
Module quicklogging.base
=========================

.. autofunction:: get_logger

.. autofunction:: _log_with_level

"""
import inspect
import logging


def get_logger(stackoverhead=0):
    """
    wrapper for getLogger

    Typical use, say you're in project/module/submodule.py and
    you want a logger.

    .. code-block:: python

        l = get_logger()
        print(l)

    .. code-block:: none

        <logging.Logger at ... >

    .. code-block:: python

        print(l.name)

    .. code-block:: none

        project.module.submodule

    :param int stackoverhead: defaults to 0. How deep to look in the stack for
        fetching the logger name.
    :return: a logger named after the module at depth ``stackoverhead``.
    :rtype: logging.Logger
    """
    frm = inspect.stack()[1 + stackoverhead]
    mod = inspect.getmodule(frm[0])

    if mod is None:
        basename = "<No module>"
    else:
        basename = mod.__name__

    return logging.getLogger(basename)


def _log_with_level(func_name, *args, **kwargs):
    """Internal convenience function to log with appropriate level

    This function is called by the main log wrappers.

    Fetches the appropriate logger, then the function named after the
    param ``func_name``. This is slow, you'd better use :py:func`get_logger`.

    :param str func_name: One of 'debug', 'info', 'error', etc
    :param int stackoverhead: defaults to 0. How deep to look in the stack for
    :rtype: None
    """
    stackoverhead = kwargs.pop('stackoverhead', 0)
    logger = get_logger(stackoverhead=stackoverhead + 1)
    logfunc = getattr(logger, func_name)
    logfunc(*args, **kwargs)
