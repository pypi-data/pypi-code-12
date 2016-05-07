#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=I0011,R0913
"""Virtual Lcd class for direct input

Example:
lcd = CharLCD(20,4, I2C(0x20, 1))
lcd = CharLCD(20,4, GPIO())
lcd = CharLCD(20,4, I2C(0x20, 1), 1, 1)
lcd = CharLCD(20,4, I2C(0x20, 1), cursor_blink=1)
"""

import charlcd.abstract.lcd_virtual as lcd
import charlcd.abstract.direct_interface as direct


class CharLCD(direct.Direct, lcd.CharLCDVirtual):
    """Virtual Lcd class for direct input"""
    def __init__(self, width, height):
        lcd.CharLCDVirtual.__init__(self,
                                    width, height,
                                    lcd.DISPLAY_MODE_DIRECT)

    def init(self):
        """Buffer init"""
        if self.initialized:
            return
        if len(self.displays) == 0:
            raise ValueError("Add lcd before init vlcd")

        for display in self.displays:
            display['lcd'].init()
        self.initialized = True

    def write(self, string, pos_x=None, pos_y=None):
        """Write string to lcd
        Args:
            string: string to display
            pos_x: x coords
            pos_y: y coords
        """
        if pos_x is not None and pos_y is not None:
            self.set_xy(pos_x, pos_y)

        for char in string:
            self._char(char)

    def _char(self, char):
        """Write char
        Args:
            char: char to display
        """
        if self.current_pos['x'] >= self.width:
            return

        self._select_active_display()

        self.current_pos['x'] += 1
        if self.active_display is None:
            return

        self.active_display['lcd'].write(char)

        if self.current_pos['x'] >= self.active_display['x'] + \
                self.active_display['width'] - 1 - \
                self.active_display['offset_x']:
            self.active_display = None

    def set_xy(self, pos_x, pos_y):
        """Set cursor position @ (x, y)
        Args:
            pos_x: x position
            pos_y: y position
        """
        lcd.CharLCDVirtual.set_xy(self, pos_x, pos_y)
        self.active_display = None

    def _stream_char(self, char):
        """Stream char on screen, following chars are put one after another.
        Restart from beginning after reaching end
        Args:
            char: char to display
        """
        self._char(char)
        self._next_cursor_position()

    def stream(self, string):
        """Stream string - use stream_char
        Args:
            string: string to display
        """
        for char in string:
            self._stream_char(char)

    def _next_cursor_position(self):
        """Calculate next position, break lines and can go back to top"""
        if self.current_pos['x'] >= self.width:
            self.current_pos['x'] = 0
            self.current_pos['y'] += 1
            self.active_display = None
            if self.current_pos['y'] >= self.height:
                self.current_pos['y'] = 0

    def _select_active_display(self):
        """Helper,
        looks for proper lcd for given coordinates, may return None
        """
        if self.active_display is None:
            self.active_display = self.get_display(
                self.current_pos['x'],
                self.current_pos['y']
            )
            if self.active_display is None:
                return
            self.active_display['lcd'].set_xy(
                self.current_pos['x'] - self.active_display['x'] +
                self.active_display['offset_x'],
                self.current_pos['y'] - self.active_display['y'] +
                self.active_display['offset_y']
            )
