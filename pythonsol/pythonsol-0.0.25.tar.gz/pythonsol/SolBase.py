"""
# -*- coding: utf-8 -*-
# ===============================================================================
#
# Copyright (C) 2013/2014/2015 Laurent Champagnac
#
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
# ===============================================================================
"""
import ast
import platform
import time
import logging
from logging.config import fileConfig
from logging.handlers import WatchedFileHandler
from threading import Lock
import traceback
import sys

import os
from gevent import monkey
import gevent

import datetime


logger = logging.getLogger("SolBase")
lifecyclelogger = logging.getLogger("lifecycle")


class SolBase(object):
    """
    Base utilities & helpers.
    """

    # ===============================
    # STATIC STUFF
    # ===============================

    # Component name (mainly for rsyslog)
    _compo_name = "CompoNotSet"

    # Global init stuff
    _voodoo_initialized = False
    _voodoo_lock = Lock()

    # Logging stuff
    _logging_initialized = False
    _logging_lock = Lock()

    # Fork stuff
    _master_process = True

    # ===============================
    # DATE & MS
    # ===============================

    @classmethod
    def mscurrent(cls):
        """
        Return current millis since epoc
        :return int
        :rtype int
        """
        return time.time() * 1000.0

    @classmethod
    def msdiff(cls, ms_start, ms_end=None):
        """
        Get difference in millis between current millis and provided millis.
        :param ms_start: Start millis
        :type ms_start: float
        :param ms_end: End millis (will use current if not provided)
        :type ms_end: float
        :return float
        :rtype float
        """

        if ms_end:
            return ms_end - ms_start
        else:
            return cls.mscurrent() - ms_start

    @classmethod
    def datecurrent(cls, erase_mode=0):
        """
        Return current date (UTC)
        :param erase_mode: Erase mode (0=nothing, 1=remove microseconds but keep millis, 2=remove millis completely)
        :return datetime
        :rtype datetime
        """

        if erase_mode == 0:
            return datetime.datetime.utcnow()
        elif erase_mode == 1:
            # Force precision loss (keep millis, kick micro)
            dt = datetime.datetime.utcnow()
            return dt.replace(microsecond=(dt.microsecond * 0.001) * 1000)
        elif erase_mode == 2:
            return datetime.datetime.utcnow().replace(microsecond=0)

    @classmethod
    def datediff(cls, dt_start, dt_end=None):
        """
        Get difference in millis between two datetime
        :param dt_start: Start datetime
        :type dt_start: datetime
        :param dt_end: End datetime (will use current utc if not provided)
        :type dt_end: datetime
        :return float
        :rtype float
        """

        # Get delta
        if dt_end:
            # noinspection PyUnresolvedReferences
            delta = dt_end - dt_start
        else:
            # noinspection PyTypeChecker
            delta = cls.datecurrent() - dt_start

        return ((delta.days * 86400 + delta.seconds) * 1000) + (delta.microseconds * 0.001)

    # ===============================
    # COMPO NAME (FOR RSYSLOG)
    # ===============================

    @classmethod
    def set_compo_name(cls, compo_name):
        """
        Set the component name. Useful for rsyslog.
        :param compo_name: The component name or None. If None, method do nothing.
        :type compo_name: str,None
        """

        if compo_name:
            cls._compo_name = compo_name
            lifecyclelogger.debug("compo_name now set to=%s", cls._compo_name)

    @classmethod
    def get_compo_name(cls):
        """
        Get current component name.
        :return str
        :rtype str
        """

        return cls._compo_name

    @classmethod
    def get_machine_name(cls):
        """
        Get machine name
        :return: Machine name
        :rtype: str
        """

        return platform.uname()[1]

    # ===============================
    # MISC
    # ===============================

    @classmethod
    def sleep(cls, sleep_ms):
        """
        Sleep for specified ms.
        Also used as gevent context switch in code, since it rely on gevent.sleep.
        :param sleep_ms: Millis to sleep.
        :type sleep_ms: int
        :return Nothing.
        """
        gevent.sleep(sleep_ms * 0.001)

    # ===============================
    # EXCEPTION HELPER
    # ===============================

    @classmethod
    def extostr(cls, e, max_level=10, max_path_level=5):
        """
        Format an exception.
        :param e: Any exception instance.
        :type e: Exception
        :param max_level: Maximum call stack level (default 10)
        :type max_level: int
        :param max_path_level: Maximum path level (default 5)
        :type max_path_level: int
        :return The exception readable string
        :rtype str
        """

        # Go
        list_frame = None
        try:
            out_buffer = ""

            # Class type
            out_buffer += "e.cls:[{0}]".format(e.__class__.__name__)

            # To string
            try:
                ex_buf = str(e)
            except UnicodeEncodeError:
                ex_buf = str(repr(unicode(e)))
            except Exception as e:
                logger.error("Exception, e=%s", e)
                raise
            out_buffer += ", e.str:[{0}]".format(ex_buf)

            # Traceback
            si = sys.exc_info()

            # Raw frame
            # tuple : (file, lineno, method, code)
            raw_frame = traceback.extract_tb(si[2])
            raw_frame.reverse()

            # Go to last tb_next
            last_tb_next = None
            cur_tb = si[2]
            while cur_tb:
                last_tb_next = cur_tb
                cur_tb = cur_tb.tb_next

            # Skip frame up to current raw frame count
            list_frame = list()
            cur_count = -1
            skip_count = len(raw_frame)
            if last_tb_next:
                cur_frame = last_tb_next.tb_frame
            else:
                cur_frame = None
            while cur_frame:
                cur_count += 1
                if cur_count < skip_count:
                    cur_frame = cur_frame.f_back
                else:
                    # Need : tuple : (file, lineno, method, code)
                    raw_frame.append((cur_frame.f_code.co_filename, cur_frame.f_lineno, cur_frame.f_code.co_name, ""))
                    cur_frame = cur_frame.f_back

            # Build it
            cur_idx = 0
            out_buffer += ", e.cs=["
            for tu in raw_frame:
                line = str(tu[1])
                cur_file = tu[0]
                method = tu[2]

                # Handle max path level
                ar_token = cur_file.rsplit(os.sep, max_path_level)
                if len(ar_token) > max_path_level:
                    # Remove head
                    ar_token.pop(0)
                    # Join
                    cur_file = "..." + os.sep.join(ar_token)

                # Format
                out_buffer += "in:{0}#{1}@{2} ".format(method, cur_file, line)

                # Loop
                cur_idx += 1
                if cur_idx >= max_level:
                    out_buffer += "..."
                    break

            # Close
            out_buffer += "]"

            # Ok
            return out_buffer
        finally:
            if list_frame:
                del list_frame

    # ===============================
    # VOODOO INIT
    # ===============================

    @classmethod
    def voodoo_init(cls, aggressive=True):
        """
        Global initialization, to call asap.
        Apply gevent stuff & default logging configuration.
        :param aggressive: bool
        :type aggressive: bool
        :return Nothing.
        """

        # Check
        if cls._voodoo_initialized:
            return

        # Lock
        with cls._voodoo_lock:
            # Re-check
            if cls._voodoo_initialized:
                return

            # Fire the voodoo magic :)
            lifecyclelogger.debug("Voodoo : gevent : entering, aggressive=%s", aggressive)
            monkey.patch_all(aggressive=aggressive)
            lifecyclelogger.debug("Voodoo : gevent : entering")

            # Initialize log level to INFO
            lifecyclelogger.debug("Voodoo : logging : entering")
            cls.logging_init()
            lifecyclelogger.debug("Voodoo : logging : done")

            # Done
            cls._voodoo_initialized = True

    # ===============================
    # LOGGING
    # ===============================

    @classmethod
    def logging_init(cls, log_level="INFO", force_reset=False, log_callback=None,
                     log_to_file=None, log_to_syslog=True, log_to_console=True):
        """
        Initialize logging sub system with default settings (console, pre-formatted output)
        :param log_to_console: if True to to console
        :type log_to_console: bool
        :param log_level: The log level to set. Any value in "DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"
        :type log_level: str
        :param force_reset: If true, logging system is reset.
        :type force_reset: bool
        :param log_to_file: If specified, log to file
        :type log_to_file: str,None
        :pram log_to_syslog: If specified, log to syslog
        :type log_to_syslog: bool
        :param log_callback: Callback for unittest
        :return Nothing.
        """

        if cls._logging_initialized and not force_reset:
            return

        with cls._logging_lock:
            if cls._logging_initialized and not force_reset:
                return

            # Default
            logging.basicConfig(level=log_level)

            # Formatter
            f = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(module)s@%(funcName)s@%(lineno)d |"
                " %(message)s | %(thread)d:%(threadName)s | %(process)d:%(processName)s")

            # Console handler
            c = None
            if log_to_console:
                c = logging.StreamHandler(sys.stdout)
                c.setLevel(logging.getLevelName(log_level))
                c.setFormatter(f)

            # File handler to /tmp
            cf = None
            if log_to_file:
                cf = WatchedFileHandler(log_to_file, encoding="utf-8")
                cf.setLevel(logging.getLevelName(log_level))
                cf.setFormatter(f)

            # Syslog handler
            syslog = None
            if log_to_syslog:
                try:
                    from pythonsol.SysLogger import SysLogger

                    syslog = SysLogger(log_callback=log_callback)
                    syslog.setLevel(logging.getLevelName(log_level))
                    syslog.setFormatter(f)
                except Exception as e:
                    raise Exception("Unable to import SysLogger, e=%s", SolBase.extostr(e))

            # Initialize
            root = logging.getLogger()
            root.setLevel(logging.getLevelName(log_level))
            root.handlers = []
            if log_to_console:
                root.addHandler(c)
            if log_to_file:
                root.addHandler(cf)
            if log_to_syslog:
                root.addHandler(syslog)

            # Done
            cls._logging_initialized = True
            if force_reset:
                lifecyclelogger.info("Logging : initialized from memory, log_level=%s, force_reset=%s",
                                     log_level, force_reset)
            else:
                lifecyclelogger.debug("Logging : initialized from memory, log_level=%s, force_reset=%s",
                                      log_level, force_reset)

    @classmethod
    def logging_initfromfile(cls, config_file_name, force_reset=False):
        """
        Initialize logging system from a configuration file, with optional reset.
        :param config_file_name: Configuration file name
        :type config_file_name: str
        :param force_reset: If true, logging system is reset.
        :type force_reset: bool
        :return Nothing.
        """

        if cls._logging_initialized and not force_reset:
            return

        with cls._logging_lock:
            if cls._logging_initialized and not force_reset:
                return

            try:
                logger.debug("Logging : config_file_name=%s", config_file_name)
                fileConfig(config_file_name, None, False)
                if force_reset:
                    lifecyclelogger.info("Logging : initialized from file, config_file_name=%s", config_file_name)
                else:
                    lifecyclelogger.debug("Logging : initialized from file, config_file_name=%s", config_file_name)
            except Exception as e:
                logger.error("Exception, e=%s", cls.extostr(e))
                raise

    # ===============================
    # FORK STUFF
    # ===============================

    @classmethod
    def get_master_process(cls):
        """
        Return True if we are the master process, False otherwise.
        :return bool
        :rtype bool
        """
        return cls._master_process

    @classmethod
    def set_master_process(cls, b):
        """
        Set is we are a fork master or not
        :param b: True if we are master process, False if we are a child process.
        :type b: bool
        :return Nothing
        """

        logger.debug("Switching _masterProcess to %s", b)
        cls._master_process = b

    # ===============================
    # BINARY STUFF
    # ===============================

    @classmethod
    def binary_to_unicode(cls, bin_buf, encoding="utf-8"):
        """
        Binary buffer to unicode, using the specified encoding
        :param bin_buf: Binary buffer
        :type bin_buf: str
        :param encoding: Encoding to use
        :type encoding: str
        :return unicode
        :rtype unicode
        """

        return unicode(bin_buf, encoding)

    @classmethod
    def unicode_to_binary(cls, unicode_buf, encoding="utf-8"):
        """
        Unicode to binary buffer, using the specified encoding
        :param unicode_buf: String to convert.
        :type unicode_buf: unicode
        :param encoding: Encoding to use.
        :type encoding: str
        :return str
        :rtype str
        """

        return unicode_buf.encode(encoding)

    # ===============================
    # CONVERSIONS
    # ===============================

    @classmethod
    def to_int(cls, v):
        """
        Convert to int
        :param v: int,str
        :type v: int,str
        :return: int
        :rtype int
        """

        if isinstance(v, int):
            return v
        else:
            return int(v)

    @classmethod
    def to_long(cls, v):
        """
        Convert to long
        :param v: long,str
        :type v: long,str
        :return: long
        :rtype long
        """

        if isinstance(v, long):
            return v
        else:
            return long(v)

    @classmethod
    def to_bool(cls, v):
        """
        Convert to bool
        :param v: bool,str
        :type v: bool,str
        :return: bool
        :rtype bool
        """

        if isinstance(v, bool):
            return v
        else:
            return ast.literal_eval(v)

    @classmethod
    def get_classname(cls, my_instance):
        """
        Return the class name of my_instance, or "Instance.None".
        :param cls: Our class.
        :param my_instance: Instance to use.
        :return: Return the class name of my_instance, or "Instance.None" in case of error/None value.
        """
        if my_instance is None:
            return "Instance.None"
        else:
            return my_instance.__class__.__name__

    @classmethod
    def get_pathseparator(cls):
        """
        Return the path separator.
        http://docs.python.org/library/os.html#os.sep
        :param cls: Our class
        :return: The path separator (string)
        """
        return os.sep

    @classmethod
    def is_string(cls, my_string):
        """
        Return true if the provided my_string is a str or an unicode.
        :param cls: Our class.
        :param my_string: A String.
        :return: Return true if the provided my_string is a str or an unicode. False otherwise.
        """
        if my_string is None:
            return False
        else:
            return isinstance(my_string, (str, unicode))

    @classmethod
    def is_string_not_empty(cls, my_string):
        """
        Return true if the provided my_string is a str or an unicode, not empty.
        :param cls: Our class.
        :param my_string: A String.
        :return: Return true if the provided my_string is a str or an unicode, not empty.. False otherwise.
        """
        if not SolBase.is_string(my_string):
            return False
        else:
            return len(my_string) > 0

    @classmethod
    def is_bool(cls, my_bool):
        """
        Return true if the provided my_bool is a boolean.
        :param cls: Our class.
        :param my_bool: A boolean..
        :return: Return true if the provided my_bool is a boolean. False otherwise.
        """
        if my_bool is None:
            return False
        else:
            return isinstance(my_bool, bool)

    @classmethod
    def is_int(cls, my_int):
        """
        Return true if the provided my_int is a integer.
        :param cls: Our class.
        :param my_int: An integer..
        :return: Return true if the provided my_int is a integer. False otherwise.
        """
        if my_int is None:
            return False
        # Caution, boolean is an integer...
        elif SolBase.is_bool(my_int):
            return False
        else:
            return isinstance(my_int, (int, long))

    @classmethod
    def get_current_pid_as_string(cls):
        """
        Return the current pids as string.
        :param cls: Our class.
        :return: A String
        """
        return "pid={0}, ppid={1}".format(os.getpid(), os.getppid())
