"""
# -*- coding: utf-8 -*-
# ===============================================================================
#
# Copyright (C) 2013/2014/2015 Laurent Champagnac
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

# Logger
import logging
import sys

from pythonsol.AtomicInt import AtomicInt
from pythonsol.DelayToCount import DelayToCount
from pythonsol.meter.MeterBase import MeterBase
from pythonsol.SolBase import SolBase


SolBase.logging_init()
logger = logging.getLogger("TcpServerStat")


class TcpServerStat(MeterBase):
    """
    Tcp server stat.
    """

    def __init__(self):
        """
        Constructor.
        """

        # ==========================
        # GENERIC
        # ==========================

        # Client connected, current
        self.client_connected = AtomicInt()

        # Client register : count
        self.client_register_count = AtomicInt()

        # Client register : exception
        self.client_register_exception = AtomicInt()

        # Client remove : count
        self.client_remove_count = AtomicInt()

        # Client remove : errors, by type
        self.client_remove_nothashed = AtomicInt()

        # Client remove : exception
        self.client_remove_exception = AtomicInt()

        # Client remove : time out
        self.client_remove_timeout_internal = AtomicInt()
        self.client_remove_timeout_business = AtomicInt()

        # ==========================
        # SEND / RECV
        # ==========================

        # Server : bytes to send, pending
        self.server_bytes_send_pending = AtomicInt()

        # Server : bytes sent
        self.server_bytes_send_done = AtomicInt()

        # Server : bytes received
        self.server_bytes_received = AtomicInt()

        # ==========================
        # SSL
        # ==========================

        # Time from accept to ssl handshake startup
        self.delay_server_accept_to_sslhandshakestart = DelayToCount("delay_server_accept_to_sslhandshakestart")

        # Time taken by ssl handshake itself (success AND timeout)
        self.delay_server_sslhandshake = DelayToCount("delay_server_sslhandshake")

        # SSL handshake timeout
        self.ssl_handshake_timeout_count = AtomicInt()

        # ==========================
        # SESSIONS
        # ==========================

        # Session duration in SECONDS (not in millis)
        self.session_duration_second = DelayToCount("session_duration_second",
                                                    ar_delay=[30, 60, 300, 1800, 3600, 14400, 28800, 86400, 172800,
                                                              sys.maxint])

    def get_namevalue_dict(self):
        """
        Return the dict for MeterManager.
        :return: A dict
        """

        d = dict()
        d["RAW-client_connected"] = self.client_connected.get()
        d["RAW-client_register_count"] = self.client_register_count.get()
        d["RAW-client_register_exception"] = self.client_register_exception.get()
        d["RAW-client_remove_count"] = self.client_remove_count.get()
        d["RAW-client_remove_nothashed"] = self.client_remove_nothashed.get()
        d["RAW-client_remove_exception"] = self.client_remove_exception.get()
        d["RAW-client_remove_timeout_business"] = self.client_remove_timeout_business.get()
        d["RAW-client_remove_timeout_internal"] = self.client_remove_timeout_internal.get()
        d["RAW-server_bytes_send_pending"] = self.server_bytes_send_pending.get()
        d["RAW-server_bytes_send_done"] = self.server_bytes_send_done.get()
        d["RAW-server_bytes_received"] = self.server_bytes_received.get()
        d["RAW-ssl_handshake_timeout_count"] = self.ssl_handshake_timeout_count.get()
        d.update(self.delay_server_accept_to_sslhandshakestart.to_dict())
        d.update(self.delay_server_sslhandshake.to_dict())
        d.update(self.session_duration_second.to_dict())
        return d

    def write_to_logger(self):
        """
        Write
        :return Nothing
        """
        logger.info("BEGIN ===")
        logger.info("client_connected=%s", self.client_connected.get())
        logger.info("client_register_count=%s", self.client_register_count.get())
        logger.info("client_register_exception=%s", self.client_register_exception.get())
        logger.info("client_remove_count=%s", self.client_remove_count.get())
        logger.info("client_remove_nothashed=%s", self.client_remove_nothashed.get())
        logger.info("client_remove_exception=%s", self.client_remove_exception.get())
        logger.info("client_remove_timeout_internal=%s", self.client_remove_timeout_internal.get())
        logger.info("client_remove_timeout_business=%s", self.client_remove_timeout_business.get())
        logger.info("server_bytes_send_pending=%s", self.server_bytes_send_pending.get())
        logger.info("server_bytes_send_done=%s", self.server_bytes_send_done.get())
        logger.info("server_bytes_received=%s", self.server_bytes_received.get())

        self.delay_server_accept_to_sslhandshakestart.log()
        self.delay_server_sslhandshake.log()
        self.session_duration_second.log()






