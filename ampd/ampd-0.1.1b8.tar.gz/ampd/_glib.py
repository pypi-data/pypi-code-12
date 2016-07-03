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


from gi.repository import GObject, GLib, Gio

from . import _scheduler, _client, _worker, _request

import socket


class PollerGLib(_scheduler.Poller):
    def __init__(self, *args, **kwargs):
        super(PollerGLib, self).__init__(*args, **kwargs)
        self.tcp_connection = self.socket = self.fd = None
        self.write_tag = self.other_tag = None
        self.cancel_connect = Gio.Cancellable.new()
        Gio.SocketClient.new().connect_to_host_async(self.host, self.port, self.cancel_connect, self.async_ready_cb)

    def close(self):
        super(PollerGLib, self).close()
        if self.cancel_connect:
            cancel_connect, self.cancel_connect = self.cancel_connect, None
            cancel_connect.cancel()
        if self.write_tag is not None:
            GLib.source_remove(self.write_tag)
        if self.other_tag is not None:
            GLib.source_remove(self.other_tag)
        if self.tcp_connection:
            self.tcp_connection.close()
        self.tcp_connection = self.socket = self.fd = None
        self.write_tag = self.other_tag = None

    def async_ready_cb(self, socket_client, task):
        if self.cancel_connect is None:
            return
        self.cancel_connect = None
        try:
            self.tcp_connection = socket_client.connect_to_host_finish(task)
        except GLib.Error as error:
            self.handle_error(error.message)
            return
        self.socket = self.tcp_connection.get_socket()
        self.socket.set_blocking(False)
        self.fd = self.socket.get_fd()
        self.sock = socket.fromfd(self.fd, 0, 0)
        self.other_tag = GLib.io_add_watch(self.fd, GLib.IO_IN | GLib.IO_ERR | GLib.IO_HUP, self.callback_other)

    def callback_write(self, fd, condition):
        if self.handle_write(self.sock):
            return True
        else:
            self.write_tag = None
            return False

    def callback_other(self, fd, condition):
        if not condition & (GLib.IO_HUP | GLib.IO_ERR):
            if self.handle_read(self.sock):
                return True
        self.handle_error()
        self.other_tag = None
        return False

    def start_writing(self):
        if self.write_tag is None:
            self.write_tag = GLib.io_add_watch(self.fd, GLib.IO_OUT, self.callback_write)


class SchedulerGLib(_scheduler.Scheduler):
    connect_and_poll = staticmethod(PollerGLib)
    add_timeout = staticmethod(GLib.timeout_add)
    remove_timeout = staticmethod(GLib.source_remove)


class ClientGLib(_client.Client, GObject.GObject):
    """
    Adds GLib scheduling and signal functionality to Client.

    GLib signals:
      client-connected
      client-disconnected(reason)
    """
    __gsignals__ = {
        'client-connected': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'client-disconnected': (GObject.SIGNAL_RUN_FIRST, None, (int, str)),
    }

    def __init__(self, coding=_client.Client._DEFAULT_CODING, coding_server='utf-8', excepthook=None):
        GObject.GObject.__init__(self)
        super(ClientGLib, self).__init__(SchedulerGLib, coding, coding_server, excepthook)
        self.ampd_worker_group.connect_loop(self._connected_cb, self._disconnected_cb)

    def _connected_cb(self):
        self.emit('client-connected')

    def _disconnected_cb(self, reason, message):
        self.emit('client-disconnected', reason, message)


class ServerPropertiesGLib(_client.ServerProperties, GObject.GObject):
    """
    Adds GLib property and signal functionality to ServerProperties.

    Assignment to volume, elapsed and option-X is reflected in the server.

    GLib signals:
      server-error(message)
    """
    current_song = GObject.property()
    status = GObject.property()
    state = GObject.property(type=str)
    volume = GObject.property(type=int)
    time = GObject.property(type=int)
    elapsed = GObject.property(type=float)
    bitrate = GObject.property(type=str)

    for option in _client.ServerProperties.OPTION_NAMES:
        locals()['option_' + option] = GObject.property(type=bool, default=False)

    __gsignals__ = {
        'server-error': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
    }

    def __init__(self, client):
        GObject.GObject.__init__(self)
        self.notify_handlers = []
        self.notify_handlers.append(self.connect('notify::volume', self.notify_volume_cb))
        self.notify_handlers.append(self.connect('notify::elapsed', self.notify_elapsed_cb))
        for option in self.OPTION_NAMES:
            self.notify_handlers.append(self.connect('notify::option-' + option, self.notify_option_cb))
        super(ServerPropertiesGLib, self).__init__(client)

    def _block(self):
        for handler in self.notify_handlers:
            self.handler_block(handler)

    def _unblock(self):
        for handler in self.notify_handlers:
            self.handler_unblock(handler)

    def _status_updated(self):
        super(ServerPropertiesGLib, self)._status_updated()
        if 'error' in self.status:
            self.emit('server-error', self.status['error'])
            _worker.worker(lambda x: (yield _request.commands_.clearerror()))(self)

    @staticmethod
    def notify_volume_cb(self, param):
        self._set_server_volume()

    @staticmethod
    @_worker.worker
    def notify_elapsed_cb(self, param):
        yield _request.commands_.seekcur(self.elapsed)

    @staticmethod
    @_worker.worker
    def notify_option_cb(self, param):
        option = param.name.split('-')[1]
        yield _request.commands_[option](int(self.get_property(param.name)))
