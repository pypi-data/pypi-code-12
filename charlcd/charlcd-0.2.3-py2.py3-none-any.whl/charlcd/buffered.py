#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=I0011,R0913
"""Lcd class for buffered input

Example:
lcd = CharLCD(20,4, I2C(0x20, 1))
lcd = CharLCD(20,4, GPIO())
lcd = CharLCD(20,4, I2C(0x20, 1), 1, 1)
lcd = CharLCD(20,4, I2C(0x20, 1), cursor_blink=1)
"""
from builtins import zip  # pylint: disable=I0011,W0622
from builtins import range  # pylint: disable=I0011,W0622

import charlcd.abstract.lcd as lcd
import charlcd.abstract.buffered_interface as buffered_interface


class CharLCD(lcd.CharLCD, buffered_interface.Buffered):
    """Class for char LCD
    Uses buffered input. Data is written to buffer and flushed
    Draw is sending only those positions that changed from previous frame"""

    def __init__(self, width, height, driver,
                 cursor_visible=1, cursor_blink=1):
        lcd.CharLCD.__init__(self, width, height, driver,
                             lcd.DISPLAY_MODE_BUFFERED, cursor_visible,
                             cursor_blink)
        self.screen = []
        self.buffer = []
        self.initialized = False
        self.dirty = False

    def init(self):
        """Screen init and buffer init"""
        if self.initialized:
            return
        lcd.CharLCD.init(self)
        self.screen = [" " * self.width] * self.height
        self.buffer = [" " * self.width] * self.height
        self.initialized = True

    def write(self, content, pos_x=None, pos_y=None):
        """Writes content into buffer at position(x,y) or current
        Will change internal position marker to reflect string write
        Args:
            content: content to write
            pos_x: x position
            pos_y: y position
        """
        if pos_x is None:
            pos_x = self.current_pos['x']
        if pos_y is None:
            pos_y = self.current_pos['y']

        if pos_x >= self.width:
            raise IndexError
        if pos_y >= self.height:
            raise IndexError

        line = self.buffer[pos_y]
        new_line = line[0:pos_x] + content + line[pos_x + len(content):]
        line = new_line[:self.width]
        self.buffer[pos_y] = line
        self.current_pos = {
            'x': pos_x + len(content),
            'y': pos_y
        }
        self.dirty = True

    def buffer_clear(self, from_x=None, from_y=None, width=None, height=None):
        """Clears buffer. Its not recommended to use parameters.
        Args:
            from_x: x position
            from_y: y position
            width: width of area
            height: height of area
        """
        if from_x is None and from_y is None:
            self.buffer = [" " * self.width] * self.height
        else:
            if height is None:
                height = self.height - from_y
            if width is None:
                width = self.width - from_x

            for pos_y in range(from_y, from_y + height):
                line = self.buffer[pos_y]
                self.buffer[pos_y] = line[0:from_x] + (" " * width) + line[from_x + width:]
        self.dirty = True

    def flush(self):
        """Flush buffer to screen, skips chars that didn't change"""
        if not self.dirty:
            return
        bag = list(
            zip(list(range(0, self.get_height())), self.buffer, self.screen)
        )
        for line, line_new, line_current in bag:
            if line_new != line_current:
                i = 0
                last_i = -1
                for char_new, char_current in zip(line_new, line_current):
                    if char_new != char_current:
                        if last_i != i:
                            self.driver.cmd(
                                self.get_line_address(line) + i,
                                self._get_enable(line)
                            )
                            last_i = i
                        self.driver.char(
                            char_new,
                            self._get_enable(line)
                        )
                        last_i += 1
                    i += 1
                self.screen[line] = line_new
        self.dirty = False

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
        self.write(char)
        self._next_cursor_position()

    def _next_cursor_position(self):
        """calculate next cursor position"""
        if self.current_pos['x'] >= self.width:
            self.current_pos['x'] = 0
            self.current_pos['y'] += 1
            if self.current_pos['y'] >= self.height:
                self.current_pos['y'] = 0
            self.set_xy(0, self.current_pos['y'])
