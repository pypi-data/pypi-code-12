#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=I0011,R0913
"""Lcd class for direct input

Example:
lcd = CharLCD(20,4, I2C(0x20, 1))
lcd = CharLCD(20,4, GPIO())
lcd = CharLCD(20,4, I2C(0x20, 1), 1, 1)
lcd = CharLCD(20,4, I2C(0x20, 1), cursor_blink=1)
"""

import charlcd.abstract.lcd as lcd
import charlcd.abstract.direct_interface as direct_interface


class CharLCD(direct_interface.Direct, lcd.CharLCD):
    """Class for char LCDs
    Uses direct input. Operates directly on lcd. What you write is what you see
    """
    def __init__(self, width, height, driver,
                 cursor_visible=1, cursor_blink=1):
        lcd.CharLCD.__init__(self, width, height, driver,
                             lcd.DISPLAY_MODE_DIRECT,
                             cursor_visible, cursor_blink)

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
            if self.current_pos['x'] >= self.width:
                return

    def _char(self, char):
        """Write char
        Args:
            char: char to display
        """
        self.driver.char(char, self._get_enable())
        self.current_pos['x'] += 1

    def _position(self, pos, enable=0):
        """Set cursor position
        Args:
            pos: hex address for new cursor position
        """
        self.driver.cmd(pos, enable)

    def set_xy(self, pos_x, pos_y):
        """Set cursor position by X Y. it recalculate position to hex address
        Args:
            pos_x: x position
            pos_y: y position
        """
        lcd.CharLCD.set_xy(self, pos_x, pos_y)
        self._position(
            self.get_line_address(pos_y) + pos_x,
            self._get_enable()
        )

    def stream(self, string):
        """Stream string - use stream_char
        Args:
            string: string to display
        """
        for char in string:
            self._stream_char(char)

    def _stream_char(self, char):
        """Stream char on screen, following chars are put one after another.
        Restart from beginning after reaching end
        Args:
            char: char to display
        """
        self._char(char)
        self._next_cursor_position()

    def _next_cursor_position(self):
        """calculate next cursor position"""
        if self.current_pos['x'] >= self.width:
            self.current_pos['x'] = 0
            self.current_pos['y'] += 1
            if self.current_pos['y'] >= self.height:
                self.current_pos['y'] = 0
            self.set_xy(0, self.current_pos['y'])
