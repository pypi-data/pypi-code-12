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


class Poller(object):
    def __init__(self, host, port, handle_read, handle_write, handle_error):
        self.host = host
        self.port = port
        self.handle_read = handle_read
        self.handle_write = handle_write
        self.handle_error = handle_error

    def close(self):
        pass


class Scheduler(object):
    @staticmethod
    def connect_and_poll(host, port, handle_read, handle_write, handle_error):
        raise NotImplementedError

    @staticmethod
    def add_timeout(timeout, callback, parameter):
        raise NotImplementedError

    @staticmethod
    def remove_timeout(handler):
        raise NotImplementedError
