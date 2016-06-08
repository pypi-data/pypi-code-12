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

"""Ctlimit implementation

I'm sorry, but the documentation of the code is still fairly poor.
Please send pull requests, if you need a better one.
"""

import time
import sys
import functools
import pprint
import os
import argparse
import pwd
import threading
import subprocess
import shlex
import shutil
import filecmp
import logging
import json
from gi.repository import GLib
from pydbus.generic import signal as dbus_signal  # avoid confusion with module signal
from pydbus.auto_names import auto_bus_name, auto_object_path
from pydbus import SessionBus, SystemBus

from .spi import get_subclasses_of
from .sddaemon import EventDrivenDaemon

LOGGER = logging.getLogger(__name__)
INF = float('inf')

_the_daemon = None


def main(argv=None):
    """Main function for ctlimit

    Run the daemon and return exit codes as specified by :manpage:`daemon(7)`.

    :param argv: a sequence of command line arguments
    :type argv: list
    :returns: a numeric exit code
    :rtype: int
    """
    global _the_daemon
    try:
        if argv is None:
            argv = sys.argv[1:]
        _the_daemon = CtLimitDaemon()
        return _the_daemon.main(argv)
    except KeyboardInterrupt:
        return 1  # LSB_3.1.1, initscripts, generic or unspecified error
    except Exception as e:
        program_name = os.path.basename(sys.argv[0])
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        raise
        return 1  # LSB_3.1.1, initscripts, generic or unspecified error


class CtLimitDaemon(EventDrivenDaemon):
    """A new style daemon, that limits the computer usage time.

    Ctlimit limits the daily usage time as configured in :file:`/etc/ctlimit.conf`
    """

    DEFAULT_CONFIG_FILE = os.path.join(EventDrivenDaemon.PACKAGE_DIR, "ctlimit_default.conf")

    # for DBus type codes see https://dbus.freedesktop.org/doc/dbus-specification.html
    dbus = """
    <node>
      <interface name='de.kruis.ctlimit1.Daemon'>
        <method name='Update'>
        </method>
        <method name='AttachPydevd'>
          <arg type='s' name='path' direction='in'/>
          <arg type='s' name='kwargs_json' direction='in'/>
        </method>
      </interface>
    </node>
    """

    def __init__(self):
        super().__init__()
        self.session_info_providers = []
        self.active_info_providers = []
        self.users = {}
        self.dbus_registrations = {}
        self.bus = None
        self.bus_name = auto_bus_name("de.kruis.ctlimit1")

    #  ###### DBus ######

    def Update(self):
        """DBus method to update the internal state"""
        LOGGER.info("DBus: updating state")
        self._on_wakeup("dbus")

    def AttachPydevd(self, path, kwargs_json):
        """DBus method to update the internal state

        :param path: path to the module :mod:`pydevd`
        :type path: str
        :param kwargs_json: a json encoded dictionary containing the
                            keyword arguments for :func:`pydevd.settrace`
                            or - for convenience - an empty string.
        :type kwargs_json: str
        """
        # I use json encoding for kwargs_json instead of a dictionary of
        # variants "a{sv}", because the command dbus-send(1) can't handle
        # nested container types.
        if path and path not in sys.path:
            sys.path.insert(0, path)
        import pydevd  # @UnresolvedImport
        kwargs = json.loads(kwargs_json or "{}")
        pydevd.settrace(**kwargs)

    #  ###### Callbacks ######

    def _on_sip_state_change(self, session_info_provider, session_event):
        user_id = session_event.user
        LOGGER.debug("Session event from %s for user_id %d active %s",
                     session_info_provider.name, user_id, session_event.is_active)
        try:
            user = self.users[user_id]
        except KeyError:
            # user is not monitored
            LOGGER.debug("Ignoring session event for user_id %d", user_id)
            return
        user.on_session_state_change(session_event)
        GLib.idle_add(self._on_wakeup, "SessionEvent")

    def start(self, event):
        self.__update_users()

        for sip in self.session_info_providers:
            try:
                sip.register()
            except Exception:
                LOGGER.exception("Failed to register the session info provider %r", sip)
            else:
                self.active_info_providers.append(sip)

    def stop(self, event, persistent_state):
        while self.active_info_providers:
            sip = self.active_info_providers.pop()
            try:
                sip.unregister()
            except Exception:
                LOGGER.exception("Failed to register the session info provider %r", sip)

        persistent_state['__timestamp__'] = str(time.time())
        persistent_state.update(('uid%d' % user_id, "%d %d" % (user.current_time, user.current_limit)) for user_id, user in self.users.items())

    def process_event(self, event, now, now_monotonic):
        # check for a date change
        last = self.last_wakeup_time
        if not self._same_accounting_period(last, now):
            # the date changed
            LOGGER.info("Date changed, resetting limits and time counters")
            for user in self.users.values():
                user.reset_time(now_monotonic)

        least_remaining_seconds = INF
        for user_id in self.users:
            user = self.users[user_id]
            remaining_seconds = user.get_remaining_seconds(now_monotonic)
            if remaining_seconds > 0 and remaining_seconds < least_remaining_seconds:
                least_remaining_seconds = remaining_seconds
            if remaining_seconds <= 0:
                LOGGER.warning("Timeout for user %s", user.name)
                user.logout(self.config['LogoutScript'], -remaining_seconds)
            else:
                user.cancel_logout()
        return least_remaining_seconds

    #  ###### utility methods ######

    def __update_users(self):
        timestamp = time.time()

        user_keys = (self.config["Users"]['users'] or '').split()
        saved_state = self.config["__saved_state__"]
        try:
            user_time_today_timestamp = float(saved_state['__timestamp__'])
        except Exception:
            user_time_today_timestamp = -1  # mark the data as outdated

        bygone_users = set(self.users)
        updates = {}

        # phase 1 collect updates and discard bygone users
        for user_key in user_keys:
            try:
                user_section = self.config[user_key]
            except KeyError:
                user_section = self.config.defaults()
            user_name = user_section.get('name', user_key)
            try:
                default_limit = user_section['seconds_per_day']
            except KeyError as e:
                LOGGER.warn("Limit 'seconds_per_day' for user %s is missing, ignoring user: %s", user_name, str(e))
                continue
            try:
                user_id = pwd.getpwnam(user_name).pw_uid
            except KeyError as e:
                LOGGER.warn("Ignoring unknown user '%s': %s", user_name, str(e))
                continue

            try:
                default_limit = int(default_limit)
            except Exception as e:
                LOGGER.warn("Limit for user %s is not an integer, ignoring user: %s", user_name, str(e))
                continue

            if default_limit <= 0:
                LOGGER.warn("Limit for user %s is not a positive integer, ignoring user: %d", user_name, default_limit)
                continue

            updates[user_id] = u = {}
            bygone_users.discard(user_id)
            try:
                user = self.users[user_id]
            except KeyError:
                LOGGER.info("Adding user %s (%d), default limit %d", user_name, user_id, default_limit)
                self.users[user_id] = user = User(user_name, default_limit)
                path = auto_object_path(self.bus_name, "User%d" % user_id)
                self.dbus_registrations[id(user)] = self.bus.register_object(path, user, None)
            else:
                if user.default_limit != default_limit:
                    # record pending updates
                    u["default_limit"] = default_limit
                    u["current_limit"] = default_limit

        # discard bygone users
        while bygone_users:
            user_id = bygone_users.pop()
            user = self.users.pop(user_id)
            registration = self.dbus_registrations.pop(id(user))
            registration.unregister()
            LOGGER.info("Removing bygone user %s (%d)", user.name, user_id)

        if user_time_today_timestamp == 0:
            # to simplify manual changes of the settings
            user_time_today_timestamp = timestamp
        if self._same_accounting_period(user_time_today_timestamp, timestamp):
            # the times are valid.
            for user_id in self.users:
                try:
                    v = saved_state['uid%d' % user_id]
                except KeyError:
                    continue
                try:
                    current_time, current_limit = map(float, v.split())
                except Exception as e:
                    LOGGER.error("Failed to parse saved state <%s> for user %s: %s", v, user_id, str(e))
                    continue
                user = self.users[user_id]
                u = updates[user_id]
                if user.current_limit != current_limit and "current_limit" not in u:
                    u["current_limit"] = current_limit
                if user.current_time != current_time:
                    u["current_time"] = current_time

        # phase 2: perform updates
        for user_id in updates:
            u = updates[user_id]
            user = self.users[user_id]
            for key in u:
                LOGGER.info("Updating user %s (%d): %s = %s", user.name, user_id, key, u[key])
                setattr(user, key, u[key])

    def _same_accounting_period(self, timestamp1, timestamp2):
        return time.localtime(timestamp1).tm_yday == time.localtime(timestamp2).tm_yday

    def _get_sip_config(self, name):
        section_name = "SIP:" + name
        if not self.config.has_section(section_name):
            self.config.add_section(section_name)
        return self.config[section_name]

    # ###### startup and configuration ######

    def get_argument_parser(self):
        from ctlimit import __version__
        program_version = "v%s" % __version__

        from ctlimit.__main__ import __doc__ as program_shortdesc
        program_shortdesc = program_shortdesc.split("\n")[1]  # @UndefinedVariable
        program_license = '''%s

  Created by Esther and Anselm Kruis.
  Copyright 2016 Esther and Anselm Kruis. All rights reserved.

  Licensed under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation; either
  version 2.1 of the License, or (at your option) any later version.

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc,)

        # Setup argument parser
        parser = argparse.ArgumentParser(description=program_license)
        parser.add_argument(
            "--daemon", action="store_true", help="Detach and become a SysV daemon [default: %(default)s]")
        parser.add_argument("-c", "--config", dest="config", action="store",
                            default="/etc/ctlimit.conf",
                            help="specify the config file [default: %(default)s]")
        parser.add_argument("--install-system-files", dest="install", action="store_true",
                            help="Install the systemd.service(5) file, the polkit(8) file, the configuration file and the state directory for ctlimit.")
        parser.add_argument("--publish-on-session-bus", dest="use_session_bus", action="store_true",
                            help="Use the DBus session bus instead of the system bus to publish ctlimit.")
        parser.add_argument("-v", "--verbose", dest="verbose", action="count",
                            help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version)
        return parser

    def install_system_files(self, conf):
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

        status_dir = conf.get('status_dir')
        if not status_dir:
            LOGGER.error("No status directory status_dir configured")
            return 1
        if os.path.isdir(status_dir):
            LOGGER.info("Status directory %s already exists", status_dir)
        elif os.path.exists(status_dir):
            LOGGER.error("Status directory %s exists, but is no directory", status_dir)
            return 1
        else:
            try:
                os.makedirs(status_dir, mode=0o700)
            except Exception as e:
                LOGGER.error("Can't create the status directory %s: %s", status_dir, str(e))
                return 1
            LOGGER.info("Successfully created the status directory %s", status_dir)

        service_src = conf.get("service_src")
        if not service_src:
            LOGGER.error("No systemd service file service_src configured")
            return 1
        if not os.path.isfile(service_src):
            LOGGER.error("Systemd service file service_src is not a file: %s", service_src)
            return 1

        service_dir = conf.get("service_dir")
        service_dir_cmd = conf.get("service_dir_cmd")
        if not service_dir and service_dir_cmd:
            args = shlex.split(service_dir_cmd)
            try:
                output = subprocess.check_output(args, stderr=subprocess.STDOUT, universal_newlines=True)
            except subprocess.CalledProcessError as e:
                LOGGER.error("Can't determine the service dir. Command <%s> failed with exit code %d and output: %s",
                             " ".join(map(shlex.quote, args)), e.returncode, e.output)
                return 1
            service_dir = output.rstrip(os.linesep)
        if not os.path.isdir(service_dir):
            LOGGER.error("Systemd service directory is not a directory: %s", service_dir)
            return 1

        dbus_policy_src = conf.get("dbus_policy_src")
        dbus_policy_dir = conf.get("dbus_policy_dir")
        if not dbus_policy_src:
            LOGGER.error("No policy file dbus_policy_src configured")
            return 1
        if not os.path.isfile(dbus_policy_src):
            LOGGER.error("Policy file dbus_policy_src is not a file: %s", dbus_policy_src)
            return 1
        if not os.path.isdir(dbus_policy_dir):
            LOGGER.error("DBus policy directory is not a directory: %s", dbus_policy_dir)
            return 1

        conf_src = conf.get("conf_src")
        conf_dir = conf.get("conf_dir")
        if not conf_src:
            LOGGER.error("No config file conf_src configured")
            return 1
        if not os.path.isfile(conf_src):
            LOGGER.error("Config file conf_src is not a file: %s", conf_src)
            return 1
        if not os.path.isdir(conf_dir):
            LOGGER.error("Configuration directory is not a directory: %s", conf_dir)
            return 1

        def inst(src, directory, description, never_overwrite=False):
            target = os.path.join(directory, os.path.basename(src))
            Desc = description[0].upper() + description[1:]
            if os.path.exists(target) and not os.path.isfile(target):
                LOGGER.error("%s file %s already exists but is not a file", Desc, target)
                return True
            if os.path.exists(target) and (never_overwrite or filecmp.cmp(src, target)):
                LOGGER.info("%s file %s is already installed in %s", Desc, src, directory)
            else:
                try:
                    shutil.copy(src, directory)
                except Exception as e:
                    LOGGER.error("Can't install the %s file: %s", description, str(e))
                    return True
                else:
                    LOGGER.info("Successfully copied %s file %s into directory %s", description, src, target)
            return False

        if (inst(service_src, service_dir, "service") or
                inst(dbus_policy_src, dbus_policy_dir, "dbus policy") or
                inst(conf_src, conf_dir, "config", never_overwrite=True)):
            return 1

        return 0

    def main(self, argv):
        # parse the command line arguments
        parser = self.get_argument_parser()
        parsed = parser.parse_args(argv)

        # load the configuration
        self.setup_configuration(parsed.config, parsed.verbose or 0)

        # eventually install the service file
        if parsed.install:
            return self.install_system_files(self.config["InstallFiles"])

        # configure the logging system
        self.configure_sd_daemon_logging()

        # create the DBus proxies
        timeout = 1000 * int(self.config['DBus'].get('timeout', '25'))
        if parsed.use_session_bus:
            self.bus = SessionBus()
            self.bus.timeout = timeout
            system_bus = SystemBus()
        else:
            self.bus = system_bus = SystemBus()
            system_bus.timeout = timeout

        # setup the session info provider(s)use_session_bus
        for sip in get_subclasses_of(AbstractSessionInfoProvider):
            try:
                sip = sip(system_bus)
                name = sip.name
                sip.config = self._get_sip_config(name)
                sip.update_state = functools.partial(self._on_sip_state_change, sip)
            except Exception:
                LOGGER.exception("Failed to initialize the session info provider %r", sip)
            else:
                self.session_info_providers.append(sip)
        LOGGER.debug("components assembled")

        if parsed.daemon:
            raise NotImplementedError("SysV daemon support is not yet implemented")

        with self.bus.publish(self.bus_name, self):
            return self.run()


class User:
    """A ctlimit user

    """
    # for DBus type codes see https://dbus.freedesktop.org/doc/dbus-specification.html
    dbus = """
    <node>
      <interface name='de.kruis.ctlimit1.User'>
        <method name='SetCurrentLimit'>
          <arg type='u' name='current_limit' direction='in'/>
        </method>
        <method name='IncreaseCurrentLimit'>
          <arg type='i' name='additional_seconds' direction='in'/>
        </method>
        <property name="Name" type="s" access="read">
        </property>
        <property name="DefaultLimit" type="u" access="read">
        </property>
        <property name="CurrentLimit" type="u" access="read">
          <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
        <property name="CurrentTime" type="u" access="read">
          <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
        </property>
      </interface>
    </node>
    """
    DBUS_INTERFACE = "de.kruis.ctlimit1.User"
    PropertiesChanged = dbus_signal()

    def __init__(self, name, default_limit):
        self.name = name
        self.default_limit = default_limit
        self.current_limit = default_limit
        self.current_time = 0.0
        self.active_since = None
        self.active_sessions = {}
        self.logout_sessions = set()
        self._cancel_logout_operations = set()

    @property
    def Name(self):
        return self.name

    @property
    def DefaultLimit(self):
        return self.default_limit

    @property
    def CurrentLimit(self):
        return self.current_limit

    @property
    def CurrentTime(self):
        self.get_remaining_seconds(SessionEvent.now())  # update self.current_time
        return self.current_time

    def SetCurrentLimit(self, current_limit):
        """DBus method to set the current limit"""
        if current_limit < 0:
            raise ValueError("current_limit must not be negative")
        if self.current_limit != current_limit:
            LOGGER.info("DBus: setting current limit for user %s to %ds", self.name, current_limit)
            self.current_limit = current_limit
            try:
                on_wakeup = _the_daemon._on_wakeup
            except Exception:
                pass  # probably during interpreter shutdown
            else:
                GLib.idle_add(on_wakeup, "dbus")
            self.PropertiesChanged(self.DBUS_INTERFACE, dict(CurrentLimit=self.current_limit), [])

    def IncreaseCurrentLimit(self, additional_seconds):
        """DBus method to increase the current limit"""
        self.SetCurrentLimit(max(self.current_limit + additional_seconds, 0))

    def on_session_state_change(self, session_event):
        if session_event.is_active:
            self.active_sessions[session_event.session_name] = dict(display=session_event.x11display,
                                                                    sid=session_event.sid)
            if self.active_since is None:
                LOGGER.info("User %s is now active", self.name)
                self.active_since = session_event.timestamp
        else:
            self.active_sessions.pop(session_event.session_name, None)
            if not self.active_sessions and self.active_since is not None:
                if self.active_since < session_event.timestamp:
                    self.current_time += session_event.timestamp - self.active_since
                LOGGER.info("User %s is now inactive", self.name)
                self.active_since = None
                self.cancel_logout()
        LOGGER.debug("User %s: todays limit=%.0f, current active seconds=%.0f",
                     self.name, self.current_limit, self.current_time)

    def get_remaining_seconds(self, timestamp):
        active_since = self.active_since
        if active_since is not None and active_since + 1 < timestamp:  # ignore very short deltas
            self.current_time += timestamp - active_since
            self.active_since = timestamp
            self.PropertiesChanged(self.DBUS_INTERFACE, dict(CurrentTime=self.current_time), [])

        LOGGER.info("User %s: todays limit=%.0f, current active seconds=%.0f",
                    self.name, self.current_limit, self.current_time)
        if active_since is None:
            return INF
        return self.current_limit - self.current_time

    def reset_time(self, timestamp):
        LOGGER.debug("resetting user: %s, new limit %.0f", self.name, self.default_limit)
        self.current_limit = self.default_limit
        self.current_time = 0.0
        self.PropertiesChanged(self.DBUS_INTERFACE, dict(CurrentLimit=self.current_limit, CurrentTime=self.current_time), [])
        if self.active_since is not None and self.active_since < timestamp:
            self.active_since = timestamp

    def logout(self, config, overtime):
        for session_name in self.active_sessions:
            if session_name in self.logout_sessions:
                continue
            self.logout_sessions.add(session_name)
            display = self.active_sessions[session_name].get("display")
            if display:
                self.logoutX11(config, session_name, display, overtime)
            else:
                LOGGER.warn("Can't logout session %s", session_name)

    def logoutX11(self, config, session_name, display, overtime):
        """Initiate the logout

        This method creates a logout thread, unless the logout is already in progress
        """
        # If the logout ocurrs immediately after thr start of the session, the session dbus is not
        # yet available. To avoid this race, wait a few seconds
        logout_thread = threading.Timer(10, self._perform_logout_X11, args=(config, session_name, display, overtime))
        logout_thread.name = "logout_user_{}_session_{}".format(self.name, session_name)
        logout_thread.daemon = True
        self._cancel_logout_operations.add(logout_thread.cancel)
        logout_thread.start()

    def _perform_logout_X11(self, config, session_name, display, overtime):
        try:
            warn1_seconds = int(config["warn1_seconds"])
            warn2_seconds = int(config["warn2_seconds"])
            max_overtime = int(config["max_overtime_seconds"])
            max_warn = max(10, max_overtime - int(overtime))
            if warn1_seconds + warn2_seconds > max_warn:
                if warn2_seconds <= max_warn:
                    warn1_seconds = max_warn - warn2_seconds
                else:
                    warn2_seconds = max_warn
                    warn1_seconds = 0

            timeout = warn1_seconds + warn2_seconds + 30
            command = config['command']
            args = shlex.split(command) + [self.name, display, str(warn1_seconds), str(warn2_seconds)]
            LOGGER.info("Calling logout script: %s", ' '.join(map(shlex.quote, args)))
            process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       close_fds=True, cwd="/", universal_newlines=True)
            # close the FD, but only once.

            def close_stdin(stdin={process.stdin}):
                try:
                    stdin = stdin.pop()
                except KeyError:
                    pass
                else:
                    stdin.close()

            # process.communicate will close stdin once input has been send.
            # But we want to keep it open. Once
            process.stdin = None

            self._cancel_logout_operations.add(close_stdin)
            try:
                output, unused_err = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                close_stdin()
                output, unused_err = process.communicate()
            except:
                process.kill()
                process.wait()
                raise
            close_stdin()
            retcode = process.poll()
            if retcode:
                GLib.idle_add(
                    LOGGER.error, "Logout script for user %s failed with exit code %d: %s", self.name, retcode, output)
            else:
                GLib.idle_add(LOGGER.info, "Logout script succeeded for user %s: %s", self.name, output)
        finally:
            self.logout_sessions.discard(session_name)

    def cancel_logout(self):
        while self._cancel_logout_operations:
            try:
                LOGGER.info("Cancel logout operation for user: %s", self.name)
                self._cancel_logout_operations.pop()()
            except Exception:
                pass


class SessionEvent:

    def __init__(self, timestamp, is_active, session_name, user, x11display, sid):
        if timestamp is None:
            timestamp = self.now()
        self.timestamp = timestamp
        self.is_active = is_active
        self.session_name = session_name
        self.user = user
        self.x11display = x11display
        self.sid = sid

    def __str__(self):
        return pprint.pformat(self.__dict__)

    @classmethod
    def now(cls):
        return time.monotonic()


class AbstractSessionInfoProvider:

    @property
    def name(self):
        return self.__class__.__name__

    config = None
    update_state = None

    def register(self):
        raise NotImplementedError

    def unregister(self):
        raise NotImplementedError
