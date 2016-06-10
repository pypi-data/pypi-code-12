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

import logging

from .. import AbstractSessionInfoProvider, SessionEvent

LOGGER = logging.getLogger(__name__)


class LogindSessionInfoProvider(AbstractSessionInfoProvider):

    def __init__(self, bus):
        super().__init__()
        self.config = None
        self.update_state = None
        self.bus = bus
        self.subscription = None
        self.session_states = {}
        self.session_infos = {}

    @staticmethod
    def unpack(dbus_property_result):
        if isinstance(dbus_property_result, tuple) and len(dbus_property_result) == 1:
            # there are different implementations of the dbus bindings. Some return an additional tuple.
            return dbus_property_result[0]
        return dbus_property_result

    def register(self):
        self.subscription = self.bus.subscribe(sender='org.freedesktop.login1',
                                               iface='org.freedesktop.DBus.Properties',
                                               signal='PropertiesChanged', signal_fired=self._signal_fired)
        act_session_path = self._get_active_session()
        if act_session_path == '/' or self._is_session_idle(act_session_path):
            return
        ses_info = self._get_session_info(act_session_path)
        self.session_infos[act_session_path] = ses_info
        self.session_states[act_session_path] = True
        e = SessionEvent(None, True, act_session_path, *ses_info)
        self.update_state(e)

    def unregister(self):
        if self.subscription is not None:
            try:
                self.subscription.unsubscribe()
            finally:
                self.subscription = None

    def _get_active_session(self, seat="/org/freedesktop/login1/seat/seat0"):
        seat = self.bus.get(".login1", seat)
        session_path = self.unpack(seat.Get('org.freedesktop.login1.Seat', 'ActiveSession'))[1]
        return session_path

    def _is_session_idle(self, session_path):
        ses = self.bus.get(".login1", session_path)
        is_idle = self.unpack(ses.Get('org.freedesktop.login1.Session', 'IdleHint'))
        return is_idle

    def _get_session_info(self, session_path):
        ses = self.bus.get(".login1", session_path)
        user_id = self.unpack(ses.Get('org.freedesktop.login1.Session', 'User'))[0]
        display = self.unpack(ses.Get('org.freedesktop.login1.Session', 'Display'))
        sid = self.unpack(ses.Get('org.freedesktop.login1.Session', 'Leader'))
        return user_id, display, sid

    def __handle_session_state_change(self, session_path, is_active, is_idle):
        if is_active is None and is_idle is None:
            return
        if is_active is None:
            is_active = self.unpack(
                self.bus.get(".login1", session_path).Get('org.freedesktop.login1.Session', 'Active'))
        if is_idle is None:
            is_idle = self._is_session_idle(session_path)

        new_state = is_active and not is_idle
        old_state = self.session_states.get(session_path)
        if new_state is not old_state:
            # the state changed. Emit the event
            LOGGER.info("logind: session state changed to %sactive for %s", "" if new_state else "in", session_path)
            try:
                ses_info = self.session_infos[session_path]
            except KeyError:
                ses_info = self._get_session_info(session_path)
                self.session_infos[session_path] = ses_info
            self.session_states[session_path] = new_state
            e = SessionEvent(None, new_state, session_path, *ses_info)
            self.update_state(e)

    def _signal_fired(self, sender, obj, iface, signal, params):
        if (iface == 'org.freedesktop.DBus.Properties' and signal == 'PropertiesChanged'):
            interface_name, changed_properties, invalidated_properties = params
        else:
            # unknown event
            LOGGER.error("Unexpected Event: iface %s, signal %s", iface, signal)
            return
        LOGGER.debug("logind: Signal PropertiesChanged from %s, interface %s, changed: %r, invalidated: %r",
                     obj, interface_name, changed_properties, invalidated_properties)
        if interface_name == "org.freedesktop.login1.Session":
            # interesting properties: Active and IdleHint
            # both are booleans. Therefore a method get can be used to
            # access the value. If the value is None, the property didn't change
            is_active = changed_properties.get('Active')
            is_idle = changed_properties.get('IdleHint')
            self.__handle_session_state_change(obj, is_active, is_idle)
        if (interface_name == "org.freedesktop.login1.Seat" and
                obj == "/org/freedesktop/login1/seat/seat0" and
                "ActiveSession" in changed_properties):
            session_path = changed_properties.get('ActiveSession')[1]
            if session_path != '/':
                self.__handle_session_state_change(session_path, True, None)
        if (interface_name == "org.freedesktop.login1.Seat" and
                obj == "/org/freedesktop/login1/seat/seat0" and
                "Sessions" in changed_properties):
            sessions = frozenset(s[1] for s in changed_properties["Sessions"])
            for ses in list(self.session_states):
                if ses not in sessions:
                    if self.session_states[ses]:
                        LOGGER.error("bygone session is still active: %s", ses)
                        self.__handle_session_state_change(ses, False, True)
                    else:
                        del self.session_infos[ses]
                        del self.session_states[ses]
                        LOGGER.info("forget bygone session %s", ses)
