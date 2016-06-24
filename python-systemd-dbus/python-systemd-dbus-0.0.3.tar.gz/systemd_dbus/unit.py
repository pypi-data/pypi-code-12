#
# Copyright (c) 2010 Mandriva
#
# This file is part of python-systemd-dbus.
#
# python-systemd-dbus is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of
# the License, or (at your option) any later version.
#
# python-systemd-dbus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import dbus
import dbus.mainloop.glib
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

from systemd_dbus.property import Property
from systemd_dbus.exceptions import SystemdError, raise_systemd_error
from systemd_dbus.job import Job


UNIT_INTERFACE = 'org.freedesktop.systemd1.Unit'
SERVICE_INTERFACE = 'org.freedesktop.systemd1.Service'


class Unit(object):
    """Abstraction class to org.freedesktop.systemd1.Unit interface"""

    def __init__(self, unit_path, extend_interface=None):
        self.__bus = dbus.SystemBus()

        self.__proxy = self.__bus.get_object(
            'org.freedesktop.systemd1',
            unit_path,)

        self.__interface = dbus.Interface(
            self.__proxy,
            UNIT_INTERFACE
        )
        self.__extend_interface = None

        if extend_interface is not None:
            self.__extend_interface = dbus.Interface(
                self.__proxy,
                extend_interface
            )

        self.__properties_interface = dbus.Interface(
            self.__proxy,
            'org.freedesktop.DBus.Properties')

        self.__properties()

    def __properties(self):
        attr_property = Property()

        properties = self.__properties_interface.GetAll(
            self.__interface.dbus_interface)

        for key, value in properties.items():
            setattr(attr_property, key, value)

        if self.__extend_interface is not None:
            extend_properties = self.__properties_interface.GetAll(
                self.__extend_interface.dbus_interface
            )
            for key, value in extend_properties.items():
                setattr(attr_property, key, value)

        setattr(self, 'properties', attr_property)

    @raise_systemd_error
    def kill(self, who, mode, signal):
        """Kill unit.

        @param who: Must be one of main, control or all.
        @param mode: Must be one of control-group, process-group, process.
        @param signal: Must be one of the well know signal number such  as
        SIGTERM(15), SIGINT(2), SIGSTOP(19) or SIGKILL(9).

        @raise SystemdError: Raised when who, mode or signal are invalid.

        @rtype: systemd_dbus.job.Job
        """
        self.__interface.KillUnit(who, mode, signal)

    @raise_systemd_error
    def reload(self, mode):
        """Reload unit.

        @param mode: Must be one of fail, replace or isolate.

        @raise SystemdError: Raised when mode is invalid.

        @rtype: systemd_dbus.job.Job
        """
        job_path = self.__interface.Reload(mode)
        job = Job(job_path)
        return job

    @raise_systemd_error
    def reload_or_restart(self, mode):
        """Reload or restart unit.

        @param mode: Must be one of fail, replace or isolate.

        @raise SystemdError: Raised when mode is invalid.

        @rtype: systemd_dbus.job.Job
        """
        job_path = self.__interface.ReloadOrRestart(mode)
        job = Job(job_path)
        return job

    @raise_systemd_error
    def reload_or_try_restart(self, mode):
        """Reload or try restart unit.

        @param mode: Must be one of fail, replace or isolate.

        @raise SystemdError: Raised when mode is invalid.

        @rtype: systemd_dbus.job.Job
        """
        job_path = self.__interface.ReloadOrTryRestart(mode)
        job = Job(job_path)
        return job

    @raise_systemd_error
    def reset_failed(self):
        self.__interface.ResetFailed()

    @raise_systemd_error
    def restart(self, mode):
        """Restart unit.

        @param mode: Must be one of fail, replace or isolate.

        @raise SystemdError: Raised when mode is invalid.

        @rtype: systemd_dbus.job.Job
        """
        job_path = self.__interface.Restart(mode)
        job = Job(job_path)
        return job

    @raise_systemd_error
    def start(self, mode):
        """Start unit.

        @param mode: Must be one of fail or replace.

        @raise SystemdError: Raised when mode is invalid.

        @rtype: systemd_dbus.job.Job
        """
        job_path = self.__interface.Start(mode)
        job = Job(job_path)
        return job

    @raise_systemd_error
    def stop(self, mode):
        """Stop unit.

        @param mode:  Must be one of fail or replace.

        @raise SystemdError: Raised when mode is invalid.

        @rtype: systemd_dbus.job.Job
        """
        job_path = self.__interface.Stop(mode)
        job = Job(job_path)
        return job

    @raise_systemd_error
    def try_restart(self, mode):
        """Try restart unit.

        @param mode: Must be one of "fail" or "replace.

        @raise SystemdError: Raised when mode is invalid.

        @rtype: L{systemd_dbus.job.Job}
        """
        job_path = self.__interface.TryRestart(mode)
        job = Job(job_path)
        return job


class Service(Unit):
    """Abstraction class to org.freedesktop.systemd1.Service interface"""

    def __init__(self, unit_path):
        super(Service, self).__init__(unit_path, SERVICE_INTERFACE)