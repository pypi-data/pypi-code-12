#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=I0011,R0913
"""Virtual Lcd class for buffered input

Example:
lcd = CharLCD(20,4, I2C(0x20, 1))
lcd = CharLCD(20,4, GPIO())
lcd = CharLCD(20,4, I2C(0x20, 1), 1, 1)
lcd = CharLCD(20,4, I2C(0x20, 1), cursor_blink=1)
"""
from builtins import range  # pylint: disable=I0011,W0622
import charlcd.abstract.lcd_virtual as lcd
import charlcd.abstract.buffered_interface as buffered_interface


class CharLCD(lcd.CharLCDVirtual, buffered_interface.Buffered):
    """Virtual Lcd class for buffered input"""
    def __init__(self, width, height):
        lcd.CharLCDVirtual.__init__(self,
                                    width, height,
                                    lcd.DISPLAY_MODE_BUFFERED)
        self.screen = []
        self.buffer = []

    def init(self):
        """Buffer init"""
        if self.initialized:
            return
        if len(self.displays) == 0:
            raise ValueError("Add lcd before init vlcd")

        self.buffer = [" " * self.width] * self.height
        for display in self.displays:
            display['lcd'].init()
        self.initialized = True

    def write(self, content, pos_x=None, pos_y=None):
        """write to buffer"""
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

        for char in content:
            self._char(char, pos_x, pos_y)
            pos_x += 1

    def _char(self, char, pos_x, pos_y):
        """Write char to proper lcd buffer
        Args:
            char: char to write
        """
        if pos_x >= self.width:
            return

        self._select_active_display(pos_x, pos_y)

        if self.active_display is None:
            return

        self.active_display['lcd'].write(
            char,
            pos_x - self.active_display['x'] + self.active_display['offset_x'],
            pos_y - self.active_display['y'] + self.active_display['offset_y']
        )

        if pos_x >= self.active_display['x'] + \
                self.active_display['width'] - 1 - \
                self.active_display['offset_x']:
            self.active_display = None

    def _select_active_display(self, pos_x, pos_y):
        """Helper, look for proper lcd for given coordinates, may return None
        Args:
            pos_x: x position
            pos_y: y position
        """
        self.active_display = self.get_display(pos_x, pos_y)

    def buffer_clear(self, from_x=None, from_y=None, width=None, height=None):
        """Clears buffer. Don't use parameters, they are for compatibility only
        Args:
            from_x: x position
            from_y: y position
            width: width of area
            height: height of area
        """
        self.buffer = [" " * self.width] * self.height

        for display in self.displays:
            display['lcd'].buffer_clear(
                display['offset_x'],
                display['offset_y'],
                display['width'] - display['offset_x'],
                display['height'] - display['offset_y']
            )

    def flush(self):
        """Flush buffer to screen, skips chars that didn't change"""
        for display in self.displays:
            display['lcd'].flush()

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
        """Calculate next position, break lines and can go back to top"""
        if self.current_pos['x'] >= self.width:
            self.current_pos['x'] = 0
            self.current_pos['y'] += 1
            self.active_display = None
            if self.current_pos['y'] >= self.height:
                self.current_pos['y'] = 0
