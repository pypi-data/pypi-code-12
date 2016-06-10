#
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Esther Kruis and Anselm Kruis
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#

"""Generic New Style Daemon Code
"""

# modules from the standard library
import signal
import time
import logging.config
import os
import re
import configparser
import numbers
import threading

# 3rd party extensions
import sdnotify                 # from PyPi
from gi.repository import GLib  # usually provided by the Linux distribution

LOGGER = logging.getLogger(__name__)
INF = float('inf')


class EventDrivenDaemon:
    """A more or less generic event driven new style daemon.

    This is the base class for a new style/systemd daemon.
    See :manpage:`daemon(7)` and :manpage:`sd-daemon(3)` for further information.
    """
    PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

    def __init__(self):
        self.config = None
        self.config_provider = None

        self._timeout_event_id = None
        self.last_wakeup_time = time.time()
        self.last_wakeup_monotonic = time.monotonic()
        self.mainloop = GLib.MainLoop()
        self.result = None
        self.main_thread = None

    #  ###### GLib Callbacks ######

    def _on_SIGHUP(self):
        GLib.idle_add(self._reconfig)
        return True

    def _on_SIGTERM(self):
        GLib.idle_add(self._shutdown)
        return True

    def _on_start(self):
        LOGGER.debug("_on_start begin")

        try:
            self.start("startup")
        except Exception:
            LOGGER.exception("start('startup') failed")

        GLib.idle_add(self._on_wakeup, "startup")

        # Tell systemd we are ready
        self.systemd_notifier.notify("READY=1")
        LOGGER.debug("_on_start done")
        return False

    def _on_wakeup(self, event):
        """Entry point for event processing
        """
        LOGGER.debug("_on_wakeup begin: %s", event)
        self._remove_timeout_event()  # remove any pending events

        now = time.time()
        now_monotonic = time.monotonic()

        try:
            timeout = self.process_event(event, now, now_monotonic)
        except Exception:
            LOGGER.exception("process_event('%s') failed", event)
            timeout = None

        if isinstance(timeout, numbers.Real) and timeout != INF and timeout > 0:
            seconds = int(timeout)
            if seconds == 0:
                seconds = 1
            LOGGER.debug("Scheduling next wake-up in %d seconds", seconds)
            self._timeout_event_id = GLib.timeout_add_seconds(seconds, self._on_wakeup, "timeout")

        self.last_wakeup_time = now
        self.last_wakeup_monotonic = now_monotonic

        LOGGER.debug("_on_wakeup end")
        return False

    def _reconfig(self):
        LOGGER.debug("_reconfig begin")
        self.systemd_notifier.notify("RELOADING=1")

        self._stop("reconfig")
        self.config_provider.load()
        self.configure_sd_daemon_logging()

        try:
            self.start("reconfig")
        except Exception:
            LOGGER.exception("start('reconfig') failed")

        GLib.idle_add(self._on_wakeup, "reconfig")

        # Tell systemd we are ready
        self.systemd_notifier.notify("READY=1")
        LOGGER.debug("_reconfig done")
        return False

    def _shutdown(self):
        LOGGER.info("_shutdown initiated")
        self._on_wakeup("shutdown")
        self._stop("shutdown")
        self.mainloop.quit()
        return False

    #  ###### utility methods ######

    def _stop(self, event):
        self._remove_timeout_event()

        key = "__saved_state__"
        saved_state = self.config[key]
        saved_state.clear()

        try:
            self.stop(event, saved_state)
        except Exception:
            LOGGER.exception("stop('%s') failed", event)

        self.config_provider.save((key,))

    def _remove_timeout_event(self):
        timeout_event_id = self._timeout_event_id
        if timeout_event_id is not None:
            self._timeout_event_id = None
            GLib.source_remove(timeout_event_id)

    # ###### to be overloaded in a subclass ######

    def start(self, event):
        """Initialize the daemon

        Called during start up and at the end of a reconfiguration.
        A subclass may overload this method.

        :param event: the event, that caused the call. One of ``startup`` or ``reconfig``.
        :type event: str
        """
        pass

    def stop(self, event, persistent_state):
        """Stop the daemon

        Called during at the start of a reconfiguration and on shutdown.
        A subclass may overload this method.

        :param event: the event, that caused the call. One of ``reconfig`` or ``shutdown``.
        :type event: str
        :param persistent_state: a mutable mapping, that persists over restarts and reconfigurations.
        :type persistent_state: :class:`collections.Mapping`
        """
        pass

    def process_event(self, event, now, now_monotonic):
        """Process an event

        Called on activation of the daemon. A subclass must overload this method.

        :param event: the event, that caused the call. One of ``start``, ``timeout``, ``reconfig``, ``shutdown``
                      or another value given to `_on_wakeup`.
        :type event: str
        :param now: the current time as returned by :func:`time.time`.
        :type now: float
        :param now_monotonic: the current monotonic time as returned by :func:`time.monotonic`.
        :type now_monotonic: float
        :param persistent_state: a mutable mapping, that persists over restarts and reconfigurations.
        :type persistent_state: :class:`collections.Mapping`
        :returns: This method must return `None` or a numeric value, that is interpreted
                  the maximum time in seconds until the next call of this method.
        :rtype: a real number
        """
        pass

    # ###### startup and configuration ######

    def new_config_parser(self):
        parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        parser.optionxform = lambda option: option  # preserve case of keys
        return parser

    def setup_configuration(self, config_name, verbosity):
        parser = self.new_config_parser()
        parser.add_section("environ")
        env = parser['environ']
        for k, v in os.environ.items():
            try:
                env[k] = v
            except Exception as e:
                if verbosity >=3:
                    # logging is not yet configured at this point. Therefore we need at least
                    # the level warning to get any output
                    LOGGER.warn("Failed to add environment variable '%s' to config['environ']: %s", k, str(e))
        parser.add_section("common")
        common = parser['common']
        common['package_dir'] = self.PACKAGE_DIR
        common['verbosity'] = str(verbosity)
        common['log_level'] = {0: 'ERROR', 1: 'WARNING', 2: 'INFO'}.get(verbosity, 'DEBUG')
        common['config_file'] = config_name

        config_provider = FileConfigProvider(parser, self.DEFAULT_CONFIG_FILE)

        config_provider.load()

        self.config_provider = config_provider
        self.config = config_provider.parser

    def configure_sd_daemon_logging(self):
        logging.config.fileConfig(self.config, disable_existing_loggers=False)
        LOGGER.debug("Logging configured")

    def run(self):
        self.main_thread = threading.current_thread()
        self.systemd_notifier = sdnotify.SystemdNotifier()
        os.environ.pop("NOTIFY_SOCKET", None)

        # prepare the main loop
        GLib.idle_add(self._on_start)
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGHUP, self._on_SIGHUP)
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, self._on_SIGTERM)

        LOGGER.debug("running main loop, pid: %d", os.getpid())
        try:
            # run the main loop
            self.mainloop.run()
        except Exception:
            LOGGER.exception("mainloop.run() failed")
        else:
            LOGGER.debug("mainloop done. Result: %s", self.result)
        return self.result


class FileConfigProvider:
    """Load and save configuration and state

    Read one or more configuration files into a
    :class:`~configparser.ConfigParser`. The configuration files
    must be utf-8 encoded.

    :param parser: the parser
    :type parser: :class:`~configparser.RawConfigParser`
    :param initial_config_file: the first / initial configuration file
    :type initial_config_file: str or a readable file object
    """

    def __init__(self, parser, initial_config_file):
        self.parser = parser
        self.initial_config_file = initial_config_file
        self.changed_event_ids = {}

    ON_LOAD_FAILURE = dict(ignore=lambda index, file_name, e: None,
                           warn=lambda index, file_name, e: LOGGER.warn(
                               "Failed to load config file %d %s: %s", index, file_name, e),
                           error=lambda index, file_name, e: LOGGER.error(
                                "Failed to load config file %d %s: %s", index, file_name, e))
    ON_LOAD_FAILURE_ERROR = ON_LOAD_FAILURE['error']

    def load(self):
        """Load the configuration files.

        The method first reads *self.initial_config_file*. If this file
        contain a section named "ConfigFiles" the method tries
        to load the configuration files given by section keys "config_file1",
        "config_file2", ... and so on. Loading stops on the first missing
        key. The optional section entries "config_on_failure1", ... govern
        the error handling. Possible values are ``ignore``, ``ẁarn`` and ``error``.
        """
        file_name = self.initial_config_file
        on_failure = self.ON_LOAD_FAILURE_ERROR
        index = 0
        while True:
            try:
                if isinstance(file_name, str):
                    with open(file_name, mode='r', encoding='utf_8') as fp:
                        self.parser.read_file(fp)
                else:
                    self.parser.read_file(file_name)
            except IOError as e:
                on_failure(index, file_name, str(e))
                if on_failure is self.ON_LOAD_FAILURE_ERROR:
                    break
            index += 1
            try:
                conf_files = self.parser['ConfigFiles']
                file_name = conf_files['config_file' + str(index)]
                on_failure = self.ON_LOAD_FAILURE.get(
                    conf_files.get('config_on_failure' + str(index), 'error'), self.ON_LOAD_FAILURE_ERROR)
            except KeyError:
                break

    def save(self, state_sections):
        """Save the state

        This method saves the sections givens in *state_sections* into
        the file specified by the entry ``status_file`` of the section
        "ConfigFiles".

        :param state_sections: an iterable of section name prefixes
        :type state_sections: class:`collections.Iterable`
        """
        parser = configparser.ConfigParser()
        parser.optionxform = self.parser.optionxform

        defaults = self.parser.defaults()
        for section_name in self.parser:
            if any(section_name.startswith(s) for s in state_sections):
                parser.add_section(section_name)
                sec = parser[section_name]
                for (k, v) in self.parser[section_name].items():
                    try:
                        default = defaults[k]
                    except KeyError:
                        pass
                    else:
                        if v is default:
                            # probably a default value
                            continue
                    sec[k] = v
                LOGGER.info("Saving state section %s: %r", section_name, dict(sec))

        with open(self.parser['ConfigFiles']['status_file'], mode='w', encoding='utf_8') as fp:
            parser.write(fp)


class SdDaemonLoggingFormatter(logging.Formatter):
    """A :class:`~logging.Formatter` for sd-daemons

    This formatter adds the log level to the log messages
    as specified in :manpage:`sd-daemon(3)`.
    """
    _START_OF_LINE_RE = re.compile(r"\n(?=.)")

    def getSdLevelPrefix(self, logging_level):
        """Convert a logging log level to a logging-prefix

        See :manpage:`sd-daemon(3)`.
        """
        if logging_level <= logging.DEBUG:
            return "<7>"  # SD_DEBUG, debug-level messages
        elif logging_level <= logging.INFO:
            return "<6>"  # SD_INFO, informational
            # return "<5>"  # SD_NOTICE, normal but significant condition
        elif logging_level <= logging.WARNING:
            return "<4>"  # SD_WARNING, warning conditions
        elif logging_level <= logging.ERROR:
            return "<3>"  # SD_ERR, error conditions
        elif logging_level <= logging.CRITICAL:
            return "<2>"  # SD_CRIT, critical conditions
        return "<1>"      # SD_ALERT, action must be taken immediately

    def format(self, record):
        # Unfortunately the SD-Daemon spec does not specify multiline or structured log messages
        text = super().format(record)
        prefix = self.getSdLevelPrefix(record.levelno)
        text = prefix + self._START_OF_LINE_RE.sub("\n" + prefix + "    ", text)
        return text
