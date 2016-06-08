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

import unittest
from pydbus import SystemBus
from gi.repository import GLib

from ctlimit.spi import logind
from ctlimit import SessionEvent


class LogindSessionInfoProviderTest(unittest.TestCase):

    def setUp(self):
        self.bus = SystemBus()
        self.spi = spi = logind.LogindSessionInfoProvider(self.bus)
        spi.config = {}
        spi.update_state = self.default_spi_update_state

    def default_spi_update_state(self, session_event):
        self.assertIsInstance(session_event, SessionEvent)

    def tearDown(self):
        pass

    def test__get_active_session(self):
        sp = self.spi._get_active_session()
        self.assertIsInstance(sp, str)
        self.assertTrue(sp.startswith('/org/freedesktop/login1/session/'))

    def test__get_active_session_invalid_seat(self):
        self.assertRaisesRegex(GLib.Error, '.*UnknownObject.*', self.spi._get_active_session,
                               seat="/org/freedesktop/login1/seat/seat9999")

    def test_register(self):
        self.assertIsNone(self.spi.subscription)
        self.fired = False

        def update_state(session_event):
            self.fired = True
            self.assertIsInstance(session_event, SessionEvent)
            self.assertIsInstance(session_event.user, int)
            print(session_event)

        self.spi.update_state = update_state
        self.addCleanup(self.spi.unregister)
        self.spi.register()

        self.assertTrue(self.fired)
        self.assertIsNotNone(self.spi.subscription)


if __name__ == "__main__":
    unittest.main()
