# coding: utf-8

# Asynchronous Music Player Daemon client library for Python

# Copyright (C) 2015 Itaï BEN YAACOV

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
Asynchronous MPD client library

Uses the GLib main event loop and python generators for asynchronous communication with a Music Player Daemon server.

A Client connects to an MPD server.
MPD commands are executed by a Worker (or several), which is created by calling a worker function and is executed by the main loop.
A Worker can be started either directly within the Client, or, for more complex applications, within a WorkerGroup.
"""


from . import errors

from ._worker import worker, Worker
from ._client import WorkerGroup, Client, ServerProperties
from ._glib import ClientGLib, ServerPropertiesGLib

from ._request import commands_, conditions


__version__ = '0.1.1b8'


__all__ = [
    '__version__',
    'errors',
    'worker', 'Worker', 'WorkerGroup',
    'Client', 'ServerProperties',
    'ClientGLib', 'ServerPropertiesGLib',
    'commands_', 'conditions',
] + list(commands_.keys()) + list(conditions.keys())

globals().update(commands_)
globals().update(conditions)
