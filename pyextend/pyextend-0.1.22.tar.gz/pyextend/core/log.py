# coding: utf-8
"""
    pyextend.core.log
    ~~~~~~~~~~~~~~~
    Implements a simple log library.

    This module is a simple encapsulation of logging module to provide a more
    convenient interface to write log. The log will both print to stdout and
    write to log file. It provides a more flexible way to set the log actions,
    and also very simple. See examples showed below:

    Example 1: Use default settings

        import log

        log.debug('hello, world')
        log.info('hello, world')
        log.error('hello, world')
        log.critical('hello, world')

    Result:
    Print all log messages to file, and only print log whose level is greater
    than ERROR to stdout. The log file is located in '/tmp/xxx.log' if the module
    name is xxx.py. The default log file handler is size-rotated, if the log
    file's size is greater than 20M, then it will be rotated.

    Example 2: Use set_logger to change settings

        # Change limit size in bytes of default rotating action
        log.set_logger(limit = 10240) # 10M

        # Use time-rotated file handler, each day has a different log file, see
        # logging.handlers.TimedRotatingFileHandler for more help about 'when'
        log.set_logger(when = 'D', limit = 1)

        # Use normal file handler (not rotated)
        log.set_logger(backup_count = 0)

        # File log level set to INFO, and stdout log level set to DEBUG
        log.set_logger(level = 'DEBUG:INFO')

        # Both log level set to INFO
        log.set_logger(level = 'INFO')

        # Change default log file name and log mode
        log.set_logger(filename = 'yyy.log', mode = 'w')

        # Change default log formatter
        log.set_logger(fmt = '[%(levelname)s] %(message)s'

    Notice: Default logger has non-filehandler, if you need log into file, please call:
            log.set_logger(filename='filename.log', with_filehandler=True)

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""

import os
import sys
import logging
import logging.handlers

_logging_funcs = ['debug', 'info', 'warning', 'error', 'critical', 'exception']
__all__ = ['set_logger', 'disable'] + _logging_funcs

# logging levels
CRITICAL = logging.CRITICAL
FATAL = logging.FATAL
ERROR = logging.ERROR
WARNING = logging.WARNING
WARN = logging.WARN
INFO = logging.INFO
DEBUG = logging.DEBUG
NOTSET = logging.NOTSET

# Color escape string
COLOR_RED = '\033[1;31m'
COLOR_GREEN = '\033[1;32m'
COLOR_YELLOW = '\033[1;33m'
COLOR_BLUE = '\033[1;34m'
COLOR_PURPLE = '\033[1;35m'
COLOR_CYAN = '\033[1;36m'
COLOR_GRAY = '\033[1;37m'
COLOR_WHITE = '\033[1;38m'
COLOR_RESET = '\033[1;0m'  # '\033[1;0m'

# Define log color
LOG_COLORS = {
    'DEBUG': COLOR_GRAY + '%s' + COLOR_RESET,  # '%s',
    'INFO': COLOR_GREEN + '%s' + COLOR_RESET,
    'WARNING': COLOR_YELLOW + '%s' + COLOR_RESET,
    'ERROR': COLOR_RED + '%s' + COLOR_RESET,
    'CRITICAL': COLOR_PURPLE + '%s' + COLOR_RESET,
    'EXCEPTION': COLOR_RED + '%s' + COLOR_RESET,
}
 
# Global logger
g_logger = None


class ColoredFormatter(logging.Formatter):
    """A colorful formatter."""

    def __init__(self, fmt=None, datefmt=None):
        logging.Formatter.__init__(self, fmt, datefmt)

    def format(self, record):
        level_name = record.levelname
        msg = logging.Formatter.format(self, record)

        msg = LOG_COLORS.get(level_name, '%s') % msg
        return msg


def add_handler(cls, level, fmt, colorful, **kwargs):
    """Add a configured handler to the global logger."""
    global g_logger
 
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.DEBUG)
 
    handler = cls(**kwargs)
    handler.setLevel(level)
 
    if colorful:
        formatter = ColoredFormatter(fmt, datefmt='%Y-%m-%d %H:%M:%S')
    else:
        formatter = logging.Formatter(fmt, datefmt='%Y-%m-%d %H:%M:%S')
 
    handler.setFormatter(formatter)
    g_logger.addHandler(handler)
 
    return handler


def add_streamhandler(level, fmt):
    """Add a stream handler to the global logger."""
    return add_handler(logging.StreamHandler, level, fmt, True)


def add_filehandler(level, fmt, filename, mode, backup_count, limit, when):
    """Add a file handler to the global logger."""
    kwargs = {}
 
    # If the filename is not set, use the default filename
    if filename is None:
        filename = getattr(sys.modules['__main__'], '__file__', 'log.py')
        filename = os.path.basename(filename.replace('.py', '.log'))
        filename = os.path.join('/tmp', filename)

    if not os.path.exists(os.path.dirname(filename)):
        os.mkdir(os.path.dirname(filename))

    kwargs['filename'] = filename
 
    # Choose the filehandler based on the passed arguments
    if backup_count == 0:  # Use FileHandler
        cls = logging.FileHandler
        kwargs['mode'] = mode
    elif when is None:  # Use RotatingFileHandler
        cls = logging.handlers.RotatingFileHandler
        kwargs['maxBytes'] = limit
        kwargs['backupCount'] = backup_count
        kwargs['mode'] = mode
    else:  # Use TimedRotatingFileHandler
        cls = logging.handlers.TimedRotatingFileHandler
        kwargs['when'] = when
        kwargs['interval'] = limit
        kwargs['backupCount'] = backup_count
 
    return add_handler(cls, level, fmt, False, **kwargs)


def init_logger(name=None):
    """Reload the global logger."""
    global g_logger
 
    if g_logger is None:
        g_logger = logging.getLogger(name=name)
    else:
        logging.shutdown()
        g_logger.handlers = []
 
    g_logger.setLevel(logging.DEBUG)


def disable(level):
    """Disable all logging calls of severity 'level' and below."""
    logging.disable(level)


def set_logger(name=None, filename=None, mode='a', level='NOTSET:NOTSET',
               fmt=
               '%(asctime)s %(filename)s:%(lineno)d [PID:%(process)-5d THD:%(thread)-5d %(levelname)-7s] %(message)s',
               # fmt='[%(levelname)s] %(asctime)s %(message)s',
               backup_count=5, limit=20480, when=None, with_filehandler=True):
    """Configure the global logger."""
    level = level.split(':')
 
    if len(level) == 1:  # Both set to the same level
        s_level = f_level = level[0]
    else:
        s_level = level[0]  # StreamHandler log level
        f_level = level[1]  # FileHandler log level
 
    init_logger(name=name)
    add_streamhandler(s_level, fmt)
    if with_filehandler:
        add_filehandler(f_level, fmt, filename, mode, backup_count, limit, when)
 
    # Import the common log functions for convenient
    import_log_funcs()


def import_log_funcs():
    """Import the common log functions from the global logger to the module."""
    global g_logger
 
    curr_mod = sys.modules[__name__]

    for func_name in _logging_funcs:
        func = getattr(g_logger, func_name)
        setattr(curr_mod, func_name, func)

 
# Set a default logger
set_logger(with_filehandler=False)
