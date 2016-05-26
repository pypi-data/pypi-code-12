#!/usr/bin/env python
''' tinylog.logger
Main class and business logic
'''
import sys
import os
import time
from datetime import datetime

LEVEL_MAP = {
    0: 'DEBUG',
    1: 'INFO',
    2: 'WARNING',
    3: 'ERROR',
    4: 'CRITICAL',
}

DEFAULT_DEACTIVATION_VAR = 'NO_LOGGING'

class Logger(object):

    def __init__(self,
            debug=None, info=None, warning=None, error=None, critical=None,
            console=None, fmt='{isotimestamp} [{level}] {message}\n',
            deactivation_var=DEFAULT_DEACTIVATION_VAR):
        '''
        :param debug: path to log which will contain all logging
        :param info: path to log which will contain info logging and higher
        :param warning: path to log which will contain warning logging and higher
        :param error: path to log which will contain error logging and higher
        :param critical: path to log which will just contain critical logging
        :param console: True or "stdout" to print to stdout, "stderr" to print to stderr
        :param fmt: log format, using variables `level`, `message`, `isotimestamp`, `unixtimestamp`, `unixmilli`, and `unixmicro` (add \\n to make it end in a newline, as expected)
        :return: logger instance, the interface to log messages
        '''
        # Array to paths which represent debug, info, and so on.
        # debug is 0 and critical is 4, so when a log level is picked when 
        # calling the logger, it will check the index into this and write to
        # the paths inside.
        self.log_paths = [[], [], [], [], []]
        if debug:
            self._set_log_paths(debug, 0)
        if info:
            self._set_log_paths(info, 1)
        if warning:
            self._set_log_paths(warning, 2)
        if error:
            self._set_log_paths(error, 3)
        if critical:
            self._set_log_paths(critical, 4)
        # initialize stdout and stderr to False, and check `console`
        self._stdout, self._stderr = False, False
        if console and console.lower() != 'stderr':
            self._stdout = True
        elif console and console.lower() == 'stderr':
            self._stderr = True
        self._format = fmt
        # Will call format with the correct kwargs based on the format chosen.
        self._format_func = self._determine_format_func(fmt)
        self.deactivation_var = deactivation_var

    def _set_log_paths(self, path, i):
        ''' Used to initialize the log paths and levels '''
        for i in range(i, len(self.log_paths)):
            self.log_paths[i] += [os.path.expanduser(path)]

    def _determine_format_func(self, fmt):
        ''' Used as a cheap optimization to not check all sorts of time formats
        when they're not used in the format.
        '''
        which = None
        for ts_str in ('{isotimestamp}', '{unixtimestamp}', '{unixmilli}',
            '{unixmicro}'):
            if ts_str in fmt:
                # using multiple timestamp formats makes me sad
                if which is not None:
                    which = ':('
                    break
                else:
                    which = ts_str[1:-1]
        # Quickest method, a timestamp isn't used.
        if which is None:
            return self._formatted_message_none
        elif which == 'isotimestamp':
            return self._formatted_message_iso
        elif which == 'unixtimestamp':
            return self._formatted_message_unix
        elif which == 'unixmilli':
            return self._formatted_message_unixmilli
        elif which == 'unixmicro':
            return self._formatted_message_unixmicro
        elif which == ':(':
            return self._formatted_message_all
        else:
            raise RuntimeError('tinylog failed to determine formatting function')

    def _isotimestamp(self):
        return datetime.now().isoformat()

    def _unixtimestamp(self):
        return int(time.time())

    def _unixmilli(self):
        return int(time.time() * 1000)

    def _unixmicro(self):
        return int(time.time() * 1000000)

    def _formatted_message_none(self, message, level):
        ''' NO timestamp involved '''
        return self._format.format(level=level, message=message)

    def _formatted_message_iso(self, message, level):
        ''' isotimestamp only '''
        return self._format.format(level=level, message=message,
                isotimestamp=self._isotimestamp())

    def _formatted_message_unix(self, message, level):
        ''' uses unix timestamp '''
        return self._format.format(level=level, message=message,
                unixtimestamp=self._unixtimestamp())

    def _formatted_message_unixmilli(self, message, level):
        ''' uses unix timestamp '''
        return self._format.format(level=level, message=message,
                unixmilli=self._unixmilli())

    def _formatted_message_unixmicro(self, message, level):
        ''' uses unix timestamp '''
        return self._format.format(level=level, message=message,
                unixmicro=self._unixmicro())

    def _formatted_message_all(self, message, level):
        ''' uses a combination of timestamps because god knows why '''
        return self._format.format(
                level=level, message=message,
                isotimestamp=self._isotimestamp(),
                unixtimestamp=self._unixtimestamp(),
                unixmilli=self._unixmilli(),
                unixmicro=self._unixmicro()
            )

    def _log(self, message, level):
        if os.getenv(self.deactivation_var) is not None:
            return
        level_str = LEVEL_MAP[level]
        formatted_msg = self._format_func(message, level_str)
        paths = self.log_paths[level]
        for path in paths:
            with open(path, 'a') as f:
                f.write(formatted_msg)
        if self._stdout:
            sys.stdout.write(formatted_msg)
        elif self._stderr:
            sys.stderr.write(formatted_msg)

    def debug(self, message):
        '''
        Writes message to all debug level logs.
        :param message: Message to log
        '''
        self._log(message, 0)

    def info(self, message):
        '''
        Writes message to all info level logs.
        :param message: Message to log
        '''
        self._log(message, 1)

    def warning(self, message):
        '''
        Writes message to all warning level logs.
        :param message: Message to log
        '''
        self._log(message, 2)

    def error(self, message):
        '''
        Writes message to all error level logs.
        :param message: Message to log
        '''
        self._log(message, 3)

    def critical(self, message):
        '''
        Writes message to all critical level logs.
        :param message: Message to log
        '''
        self._log(message, 4)
