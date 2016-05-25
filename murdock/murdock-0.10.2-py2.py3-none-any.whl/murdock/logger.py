# -*- coding: utf-8 -*-
#
#   This file is part of the Murdock project.
#
#   Copyright 2016 Malte Lichtner
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
Module :mod:`murdock.logger`
----------------------------

A logger interface based on the `logging` module (standard lib).

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os
import socket
import sys
import time


class Logger(object):
    """Configuration class for logging with the logging module.
    """

    def __init__(
            self, name=None, filename=None, logdir='.',
            file_level=logging.INFO, console_level=None):
        if name is not None:
            self.logger = logging.getLogger(name)
        else:
            self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.logger.logger = self
        self.ch = None
        self.fh = None
        self.name = name
        self.filepath = None
        if filename is not None:
            self.add_file_handler(file_level, logdir, filename)
        if console_level is not None:
            self.add_console_handler(console_level)

    def add_console_handler(self, level):
        """Add console handler to the logger.
        """
        self.ch = logging.StreamHandler(sys.stdout)
        self.ch.setLevel(level)
        f = custom_formatter_console()
        f.formatTime = custom_formatTime_console
        self.ch.setFormatter(f)
        self.logger.addHandler(self.ch)
        return True

    def add_file_handler(self, level, logdir, filename):
        """Add file handler to the logger.
        """
        if not os.path.exists(logdir):
            os.makedirs(logdir)
        filepath = os.path.join(os.path.abspath(logdir), filename)
        self.fh = logging.FileHandler(filepath, encoding='UTF-8')
        self.fh.setLevel(level)
        f = custom_formatter_file()
        f.formatTime = custom_formatTime_file
        self.fh.setFormatter(f)
        self.logger.addHandler(self.fh)
        return True

    def shutdown(self):
        """Closes all logging handlers.

        No further use of the logging system can/should be made after calling
        this method.

        """
        if self.fh is not None:
            self.fh.flush()
        if self.ch is not None:
            self.ch.flush()
        logging.shutdown()
        return True

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warn(self, msg):
        self.logger.warn(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)


def custom_formatter_console():
    """Return custom console log formatter.
    """
    fmt = '%(asctime)s %(levelname)-8s %(message)s'
    return logging.Formatter(fmt=fmt)


def custom_formatter_file():
    """Return custom file log formatter.
    """
    fmt = '[{hostname}:%(process)d] %(asctime)s %(levelname)-8s %(message)s'
    return logging.Formatter(fmt=fmt.format(hostname=socket.gethostname()))


def custom_formatTime_console(record, datefmt=None):
    """Customize timing output for a console log record.

    Overrides a `logging.Formatter.formatTime` method in order to customize
    timing output for a log record. The string returned will appear in the
    output exactly where `%(asctime)s` is placed in the log format string.

    """
    return '%s.%03d' % (
        time.strftime('%H:%M:%S', time.localtime()), record.msecs)


def custom_formatTime_file(record, datefmt=None):
    """Customize timing output for a file log record.

    Overrides a `logging.Formatter.formatTime` method in order to customize
    timing output for a log record. The string returned will appear in the
    output exactly where `%(asctime)s` is placed in the log format string.

    """
    return '%s' % time.strftime('%y-%m-%d %H:%M:%S', time.localtime())
