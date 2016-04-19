# coding=utf-8
# pynput
# Copyright (C) 2015-2016 Moses Palmér
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import contextlib
import ctypes
import six
import threading

from ctypes import windll, wintypes

from . import AbstractListener


SendInput = windll.user32.SendInput
VkKeyScan = windll.user32.VkKeyScanW

GetCurrentThreadId = windll.kernel32.GetCurrentThreadId


class MessageLoop(object):
    """A class representing a message loop.
    """
    #: The message that signals this loop to terminate
    WM_STOP = 0x0401

    _GetMessage = windll.user32.GetMessageW
    _PeekMessage = windll.user32.PeekMessageW
    _PostThreadMessage = windll.user32.PostThreadMessageW

    PM_NOREMOVE = 0

    def __init__(
            self,
            initialize=lambda message_loop: None,
            finalize=lambda message_loop: None):
        self._threadid = None
        self._initialize = initialize
        self._finalize = finalize
        self._event = threading.Event()
        self.thread = None

    def __iter__(self):
        """Initialises the message loop and yields all messages until
        :meth:`stop` is called.

        :raises AssertionError: if :meth:`start` has not been called
        """
        assert self._threadid is not None

        try:
            # Pump messages until WM_STOP
            while True:
                msg = wintypes.MSG()
                lpmsg = ctypes.byref(msg)
                r = self._GetMessage(lpmsg, None, 0, 0)
                if r <= 0 or msg.message == self.WM_STOP:
                    break
                else:
                    yield msg

        finally:
            self._finalize(self)
            self._threadid = None
            self.thread = None

    def start(self):
        """Starts the message loop.

        This method must be called before iterating over messages, and it must
        be called from the same thread.
        """
        self._threadid = GetCurrentThreadId()
        self.thread = threading.current_thread()

        # Create the message loop
        msg = wintypes.MSG()
        lpmsg = ctypes.byref(msg)
        self._PeekMessage(lpmsg, None, 0x0400, 0x0400, self.PM_NOREMOVE)

        # Let the called perform initialisation
        self._initialize(self)

        # Set the event to signal to other threads that the loop is created
        self._event.set()

    def stop(self):
        """Stops the message loop.
        """
        self._event.wait()
        self._PostThreadMessage(self._threadid, self.WM_STOP, 0, 0)
        if self.thread.ident != threading.current_thread().ident:
            self.thread.join()


class SystemHook(object):
    """A class to handle Windows hooks.
    """
    _SetWindowsHookEx = windll.user32.SetWindowsHookExW
    _UnhookWindowsHookEx = windll.user32.UnhookWindowsHookEx
    _CallNextHookEx = windll.user32.CallNextHookEx

    _HOOKPROC = ctypes.WINFUNCTYPE(
        wintypes.LPARAM,
        ctypes.c_int32, wintypes.WPARAM, wintypes.LPARAM)

    #: The registered hook procedures
    _HOOKS = {}

    #: The hook action value for actions we should check
    HC_ACTION = 0

    def __init__(self, hook_id, on_hook=lambda code, msg, lpdata: None):
        self.hook_id = hook_id
        self.on_hook = on_hook
        self._hook = None

    def __enter__(self):
        key = threading.current_thread().ident
        assert key not in self._HOOKS

        # Add ourself to lookup table and install the hook
        self._HOOKS[key] = self
        self._hook = self._SetWindowsHookEx(
            self.hook_id,
            self._handler,
            None,
            0)

        return self

    def __exit__(self, type, value, traceback):
        key = threading.current_thread().ident
        assert key in self._HOOKS

        if self._hook is not None:
            # Uninstall the hook and remove ourself from lookup table
            self._UnhookWindowsHookEx(self._hook)
            del self._HOOKS[key]

    @staticmethod
    @_HOOKPROC
    def _handler(code, msg, lpdata):
        key = threading.current_thread().ident
        self = SystemHook._HOOKS.get(key, None)
        try:
            if self:
                self.on_hook(code, msg, lpdata)

        finally:
            # Always call the next hook
            return SystemHook._CallNextHookEx(0, code, msg, lpdata)


class MOUSEINPUT(ctypes.Structure):
    """Contains information about a simulated mouse event.
    """
    MOVE = 0x0001
    LEFTDOWN = 0x0002
    LEFTUP = 0x0004
    RIGHTDOWN = 0x0008
    RIGHTUP = 0x0010
    MIDDLEDOWN = 0x0020
    MIDDLEUP = 0x0040
    XDOWN = 0x0080
    XUP = 0x0100
    WHEEL = 0x0800
    HWHEEL = 0x1000
    ABSOLUTE = 0x8000

    XBUTTON1 = 0x0001
    XBUTTON2 = 0x0002

    _fields_ = [
        ('dx', wintypes.LONG),
        ('dy', wintypes.LONG),
        ('mouseData', wintypes.DWORD),
        ('dwFlags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.c_void_p)]


class KEYBDINPUT(ctypes.Structure):
    """Contains information about a simulated keyboard event.
    """
    EXTENDEDKEY = 0x0001
    KEYUP = 0x0002
    SCANCODE = 0x0008
    UNICODE = 0x0004

    _fields_ = [
        ('wVk', wintypes.WORD),
        ('wScan', wintypes.WORD),
        ('dwFlags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.c_void_p)]


class HARDWAREINPUT(ctypes.Structure):
    """Contains information about a simulated message generated by an input
    device other than a keyboard or mouse.
    """
    _fields_ = [
        ('uMsg', wintypes.DWORD),
        ('wParamL', wintypes.WORD),
        ('wParamH', wintypes.WORD)]


class INPUT_union(ctypes.Union):
    """Represents the union of input types in :class:`INPUT`.
    """
    _fields_ = [
        ('mi', MOUSEINPUT),
        ('ki', KEYBDINPUT),
        ('hi', HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    """Used by :attr:`SendInput` to store information for synthesizing input
    events such as keystrokes, mouse movement, and mouse clicks.
    """
    MOUSE = 0
    KEYBOARD = 1
    HARDWARE = 2

    _fields_ = [
        ('type', wintypes.DWORD),
        ('value', INPUT_union)]


class ListenerMixin(object):
    """A mixin for *win32* event listeners.

    Subclasses should set a value for :attr:`_EVENTS` and implement
    :meth:`_handle`.

    Subclasses must also be decorated with a decorator compatible with
    :meth:`pynput._util.NotifierMixin._receiver` or implement the method
    ``_receive()``.
    """
    #: The Windows hook ID for the events to capture
    _EVENTS = None

    def _run(self):
        self._message_loop = MessageLoop()
        with self._receive():
            self._mark_ready()
            self._message_loop.start()

            with SystemHook(self._EVENTS, self._handler):
                # Just pump messages
                for msg in self._message_loop:
                    if not self.running:
                        break

    def _stop(self):
        try:
            self._message_loop.stop()
        except AttributeError:
            # The loop may not have been created
            pass

    @AbstractListener._emitter
    def _handler(self, code, msg, lpdata):
        """The callback registered with *Windows* for events.

        This method will call the callbacks registered on initialisation.
        """
        self._handle(code, msg, lpdata)

    def _handle(self, code, msg, lpdata):
        """The device specific callback handler.

        This method calls the appropriate callback registered when this
        listener was created based on the event.
        """
        raise NotImplementedError()


class KeyTranslator(object):
    """A class to translate virtual key codes to characters.
    """
    _AttachThreadInput = ctypes.windll.user32.AttachThreadInput
    _GetForegroundWindow = ctypes.windll.user32.GetForegroundWindow
    _GetKeyboardLayout = ctypes.windll.user32.GetKeyboardLayout
    _GetKeyboardState = ctypes.windll.user32.GetKeyboardState
    _GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
    _MapVirtualKeyEx = ctypes.windll.user32.MapVirtualKeyExW
    _ToUnicodeEx = ctypes.windll.user32.ToUnicodeEx

    _MAPVK_VK_TO_VSC = 0
    _MAPVK_VK_TO_CHAR = 2

    def __init__(self):
        self.__state = (ctypes.c_byte * 255)()
        self._cache = {}
        self._reinject_arguments = None

    def __call__(self, vk, is_press):
        """Converts a virtual key code to a string.

        :param int vk: The virtual key code.

        :param bool is_press: Whether this is a press. Because the *win32*
            functions used to translate the key modifies internal kernel state,
            some cleanup must be performed for key presses.

        :return: parameters suitable for the :class:`pynput.keyboard.KeyCode`
            constructor

        :raises OSError: if a call to any *win32* function fails
        """
        # Get the keyboard state and layout
        state, layout = self._get_state_and_layout()

        # Get the scan code for the virtual key
        scan = self._to_scan(vk, layout)

        # Try to reuse the previous key in the cache
        try:
            if is_press:
                return self._cache[vk]
            else:
                return self._cache.pop(vk)
        except KeyError:
            pass

        # Get a string representation of the key
        char, is_dead = self._to_char(vk, layout)
        modified_char = self._to_char_with_modifiers(vk, layout, scan, state)

        # Clear the keyboard state if the key was a dead key
        if is_dead:
            self._reset_state(vk, layout, scan)

        # If the previous key handled was a dead key, we reinject it
        if self._reinject_arguments:
            self._reinject(*self._reinject_arguments)
            self._reinject_arguments = None

        # If the current key is a dead key, we store the current state to be
        # able to reinject later
        elif is_dead:
            self._reinject_arguments = (
                vk,
                layout,
                scan,
                (ctypes.c_byte * 255)(*state))

        # Otherwise we just clear any previous dead key state
        else:
            self._reinject_arguments = None

        # Update the cache
        self._cache[vk] = {
            'char': modified_char or char,
            'is_dead': is_dead,
            'vk': vk}

        return self._cache[vk]

    def _get_state_and_layout(self):
        """Returns the keyboard state and layout.

        The state is read from the currently active window if possible. It is
        kept in a cache, so any call to this method will invalidate return
        values from previous invocations.

        :return: the tuple ``(state, layout)``
        """
        # Get the state of the keyboard attached to the active window
        with self._thread_input() as active_thread:
            if not self._GetKeyboardState(ctypes.byref(self.__state)):
                raise OSError(
                    'GetKeyboardState failed: %d',
                    ctypes.wintypse.get_last_error())

        # Get the keyboard layout for the thread for which we retrieved the
        # state
        layout = self._GetKeyboardLayout(active_thread)

        return (self.__state, layout)

    def _to_scan(self, vk, layout):
        """Retrieves the scan code for a virtual key code.

        :param int vk: The virtual key code.

        :param layout: The keyboard layout.

        :return: the scan code
        """
        return self._MapVirtualKeyEx(
            vk, self._MAPVK_VK_TO_VSC, layout)

    def _to_char(self, vk, layout):
        """Converts a virtual key by simply mapping it through the keyboard
        layout.

        This method is stateless, so any active shift state or dead keys are
        ignored.

        :param int vk: The virtual key code.

        :param layout: The keyboard layout.

        :return: the string representation of the key, or ``None``, and whether
            was dead as the tuple ``(char, is_dead)``
        """
        # MapVirtualKeyEx will yield a string representation for dead keys
        flags_and_codepoint = self._MapVirtualKeyEx(
            vk, self._MAPVK_VK_TO_CHAR, layout)
        if flags_and_codepoint:
            return (
                six.unichr(flags_and_codepoint & 0xFFFF),
                bool(flags_and_codepoint & (1 << 31)))
        else:
            return (None, None)

    def _to_char_with_modifiers(self, vk, layout, scan, state):
        """Converts a virtual key by mapping it through the keyboard layout and
        internal kernel keyboard state.

        This method is stateful, so any active shift state and dead keys are
        applied. Currently active dead keys will be removed from the internal
        kernel keyboard state.

        :param int vk: The virtual key code.

        :param layout: The keyboard layout.

        :param int scan: The scan code of the key.

        :param state: The keyboard state.

        :return: the string representation of the key, or ``None``
        """
        # This will apply any dead keys and modify the internal kernel keyboard
        # state
        out = (ctypes.wintypes.WCHAR * 5)()
        count = self._ToUnicodeEx(
            vk, scan, ctypes.byref(state), ctypes.byref(out),
            len(out), 0, layout)

        return out[0] if count > 0 else None

    def _reset_state(self, vk, layout, scan):
        """Clears the internal kernel keyboard state.

        This method will remove all dead keys from the internal state.

        :param int vk: The virtual key code.

        :param layout: The keyboard layout.

        :param int scan: The scan code of the key.
        """
        state = (ctypes.c_byte * 255)()
        out = (ctypes.wintypes.WCHAR * 5)()
        while self._ToUnicodeEx(
                vk, scan, ctypes.byref(state), ctypes.byref(out),
                len(out), 0, layout) < 0:
            pass

    def _reinject(self, vk, layout, scan, state):
        """Reinjects the previous dead key.

        This must be called if ``ToUnicodeEx`` has been called, and the
        previous key was a dead one.

        :param int vk: The virtual key code.

        :param layout: The keyboard layout.

        :param int scan: The scan code of the key.

        :param state: The keyboard state.
        """
        out = (ctypes.wintypes.WCHAR * 5)()
        self._ToUnicodeEx(
            vk, scan, ctypes.byref(state), ctypes.byref(out),
            len(out), 0, layout)

    @contextlib.contextmanager
    def _thread_input(self):
        """Temporarily attaches the input handling of this thread to that of
        the currently active window.

        The context manager returns the ID of the thread to which the input
        handling is attached. This is the ID of the current thread if attaching
        failed.
        """
        remote_thread = self._GetWindowThreadProcessId(
            self._GetForegroundWindow(),
            None)
        local_thread = GetCurrentThreadId()

        if self._AttachThreadInput(local_thread, remote_thread, True):
            try:
                yield remote_thread
            finally:
                self._AttachThreadInput(local_thread, remote_thread, False)
        else:
            yield local_thread
