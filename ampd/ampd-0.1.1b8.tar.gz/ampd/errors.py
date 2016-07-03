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


class Error(Exception):
    def __repr__(self):
        return self.__class__.__name__ + ': ' + super(Error, self).__repr__()

    def __str__(self):
        return self.__class__.__name__ + ': ' + super(Error, self).__str__()


class DisconnectError(Error):
    """Client disconnected while request is being processed"""

    def __init__(self, reason, message):
        self.reason = reason
        self.message = message


class ConnectionError(Error):
    pass


class ReplyError(Error):
    pass


class ProtocolError(Error):
    pass


class CommandError(Error):
    pass


class DeprecationWarning(Warning):
    pass
