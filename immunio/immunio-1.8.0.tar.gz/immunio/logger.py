"""Extension to the Python logging module."""

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import os
import sys
import time
import logging

from immunio.deps.cloghandler import ConcurrentRotatingFileHandler
from immunio.util import mkdir_p


# Custom log levels.
TRACE = logging.DEBUG - 1


class Logger(logging.Logger):
    """Logger that support our custom log levels."""

    def trace(self, msg, *args, **kwargs):
        if self.isEnabledFor(TRACE):
            self._log(TRACE, msg, args, **kwargs)


class LoggerWrapper(object):
    """Changes the logger instance.

    Other modules will import the log instance from this module, so this
    wrapper makes it possible to change the logger instance in other
    modules by replacing the logger attribute.
    """

    def __init__(self, logger=None):
        if logger is not None:
            self._logger = logger
        else:
            self.reset()

    def __getattr__(self, key):
        return getattr(self._logger, key)

    def __setattr__(self, key, value):
        if key == "_logger":
            self.__dict__["_logger"] = value
            return value
        else:
            return setattr(self._logger, key, value)

    def reset(self, log_file=None, log_level="TRACE"):
        """Reset the logger to use the startup handler."""
        handler = make_logger_handler(log_file, log_level)

        # Set the global log.
        self._logger = Logger("immunio")
        self._logger.addHandler(handler)

    def switch(self, log_file, log_level):
        """Switch to a real logger with a log file and log level.

        The messages saved in the startup logger will be emitted to the
        real logger.
        """
        # Get records from old handlers.
        records = []
        for old_handler in self._logger.handlers:
            if isinstance(old_handler, LoggerStartupHandler):
                records.extend(old_handler.records)

        self.reset(log_file, log_level)

        # Put records to new handlers.
        for new_handler in self._logger.handlers:
            for record in records:
                if record.levelno >= new_handler.level:
                    new_handler.emit(record)


class LoggerStartupHandler(logging.Handler, object):
    """Saves log records at startup.

    Before getting the log file and log level, we might want to log
    some messages. This handler saves those messages until we have a
    real handler.
    """

    def __init__(self):
        super(LoggerStartupHandler, self).__init__()
        self.records = []

    def emit(self, record):
        """See `Handler`."""
        self.records.append(record)


class LoggerFormatter(logging.Formatter, object):
    """Formatter encoding our preferred output format."""

    def __init__(self, fmt=None, datefmt=None):
        if fmt is None:
            fmt = ("%(asctime)s.%(msecs)03dZ %(name)s %(levelname)-7s: "
                   "%(message)s")
        if datefmt is None:
            datefmt = "%Y-%m-%dT%H:%M:%S"
        super(LoggerFormatter, self).__init__(fmt, datefmt)
        self.converter = time.gmtime  # Output should be UTC


def make_logger_handler(log_file, log_level):
    """Factory for making a log handler consistently.

    :param log_file: Path to the log file, or STDOUT, or STDERR.
    :returns: A log handler with formatter.
    """
    if log_file is None:
        handler = LoggerStartupHandler()
    elif log_file == "STDOUT":
        handler = logging.StreamHandler(sys.stdout)
    elif log_file == "STDERR":
        handler = logging.StreamHandler(sys.stderr)
    elif log_file == "SYSLOG":
        # Detect which platform we're running on to choose the syslog socket.
        if sys.platform == "darwin":
            syslog_file = "/var/run/syslog"
        else:
            syslog_file = "/dev/log"

        handler = logging.handlers.SysLogHandler(syslog_file)
    else:
        real_path = os.path.abspath(os.path.expanduser(log_file))
        try:
            mkdir_p(os.path.dirname(real_path))
            handler = ConcurrentRotatingFileHandler(real_path)
            log_file = real_path
        except (IOError, OSError,) as error:
            log.warn("Failed to open %s (%s) for logging (%s)",
                log_file, real_path, str(error))
            handler = logging.StreamHandler(sys.stderr)
            log_file = "STDERR"

    # We don't call logging.addLevelName to avoid potentially overwriting
    # another TRACE level name with a different TRACE level number, so we
    # have to check for the name explicitly.
    if log_level.upper() == "TRACE":
        level_number = TRACE
    else:
        level_number = logging.getLevelName(log_level.upper())
        if not isinstance(level_number, int):
            level_number = logging.DEBUG
            log.debug(
                "Failed to interpret log level %s falling back to debug",
                log_level)

    # Set the formatter and level.
    formatter = LoggerFormatter()
    handler.setFormatter(formatter)
    handler.setLevel(level_number)

    if log_file is not None:
        log.debug("Logging to %s", log_file)

    return handler


# Logger instance to be used throughout immunio code.
log = LoggerWrapper()
