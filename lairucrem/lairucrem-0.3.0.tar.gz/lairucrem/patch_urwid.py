#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""Patch urwid to support 1.2.1 which is available in Debian jessie"""

from urwid import signals
from urwid.display_common import INPUT_DESCRIPTORS_CHANGED
from urwid.main_loop import MainLoop
from .utils import monkeypatch

# pyint, that's not my code. It shall be removed once Debian updates python-urwid
#pylint: disable=bad-continuation
#pylint: disable=dangerous-default-value
#pylint: disable=protected-access

@monkeypatch(MainLoop)
def _reset_input_descriptors(self, only_remove=False, fd_handles=[]):
    """Reset input descriptors"""
    for handle in fd_handles:
        self.event_loop.remove_watch_file(handle)
    if only_remove:
        del fd_handles[:]
    else:
        fd_handles[:] = [
            self.event_loop.watch_file(fd, self._update)
            for fd in self.screen.get_input_descriptors()]
    if not fd_handles and self._input_timeout is not None:
        self.event_loop.remove_alarm(self._input_timeout)

@monkeypatch(MainLoop)
def start(self):
    """register handler to event loop"""
    assert not getattr(self, 'idle_handle', None), 'mainloop already running'
    if self.handle_mouse:
        self.screen.set_mouse_tracking()

    if not hasattr(self.screen, 'get_input_descriptors'):
        return self._run_screen_event_loop()

    self.draw_screen()

    try:
        signals.connect_signal(self.screen, INPUT_DESCRIPTORS_CHANGED,
            self._reset_input_descriptors)
    except NameError:
        pass
    # watch our input descriptors
    self._reset_input_descriptors()
    self.idle_handle = self.event_loop.enter_idle(self.entering_idle)

@monkeypatch(MainLoop)
def stop(self):
    """unregister handlers from the event loop"""
    # tidy up
    assert getattr(self, 'idle_handle', None), 'mainloop not running'
    self.event_loop.remove_enter_idle(self.idle_handle)
    del self.idle_handle
    self._reset_input_descriptors(True)
    signals.disconnect_signal(self.screen, INPUT_DESCRIPTORS_CHANGED,
        self._reset_input_descriptors)

@monkeypatch(MainLoop)
def _run(self):
    """Run the mainloop"""
    self.start()
    self.event_loop.run()
    self.stop()
