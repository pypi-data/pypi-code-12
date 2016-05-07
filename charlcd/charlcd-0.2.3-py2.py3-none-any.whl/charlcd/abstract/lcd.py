#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=I0011,R0913,R0902
"""Main lcd class"""

import time

LINE0 = 0x80
LINE1 = 0xC0
LINE2 = 0x94
LINE3 = 0xD4
LCD_LINES = [
    LINE0,
    LINE1,
    LINE2,
    LINE3
]

DISPLAY_MODE_DIRECT = 'direct'
DISPLAY_MODE_BUFFERED = 'buffered'


class CharLCD(object):
    """Class for char LCDs
        Shouldn't be instanced - use lcd_buffered or lcd_direct
    """
    def __init__(self, width, height, driver, display_mode=DISPLAY_MODE_DIRECT,
                 cursor_visible=1, cursor_blink=1):
        """Inits lcd class
        Args:
            width (int): width of lcd
            height (int): height of lcd
            driver: driver to use for lcd communication (i2c, gpio, null)
            display_mode: automatically set by calling
                lcd_direct or lcd_buffered
            cursor_visible: set show cursor
            cursor_blink: set cursor blink
        """
        self.width = width
        self.height = height
        self.driver = driver
        self.current_pos = {
            'x': 0,
            'y': 0
        }
        self.display_mode = display_mode
        self.cursor_blink = cursor_blink
        self.cursor_visible = cursor_visible
        self.twin_lcd = False  # are we using 40x4 = 2* 20x4 lcd ?
        if self.driver.pins['E2'] is not None:
            self.twin_lcd = True

    def init(self):
        """Inits lcd display, send commands"""
        self.driver.init()
        self._init(0)
        if self.is_twin():
            self._init(1)

    def _init(self, enable):
        """subroutine to init lcd"""
        self.driver.cmd(3, enable)
        time.sleep(0.05)
        self.driver.cmd(3, enable)
        time.sleep(0.05)
        self.driver.cmd(3, enable)
        time.sleep(0.05)
        self.driver.cmd(2, enable)
        self.driver.set_mode(4)
        self.driver.cmd(0x28, enable)
        self.driver.cmd(0x08, enable)
        self.driver.cmd(0x01, enable)
        self.driver.cmd(0x06, enable)
        self.driver.cmd(12 +
                        (self.cursor_visible * 2) +
                        (self.cursor_blink * 1), enable)

    def get_width(self):
        """returns lcd width"""
        return self.width

    def get_height(self):
        """return lcd height"""
        return self.height

    def get_display_mode(self):
        """return display mode, direct or buffered"""
        return self.display_mode

    def shutdown(self):
        """call shutdown on driver"""
        self.driver.shutdown()

    def write(self, string, pos_x=None, pos_y=None):
        """Writes content at position(x,y) or current
        Will change internal position marker to reflect string write
        Args:
            content: content to write
            pos_x: x position
            pos_y: y position
        """
        raise NotImplementedError("string not implemented")

    def set_xy(self, pos_x, pos_y):
        """Set cursor position to (x, y)
        Args:
            pos_x: x position
            pos_y: y position
        """
        if pos_x >= self.width or pos_x < 0:
            raise IndexError
        if pos_y >= self.height or pos_y < 0:
            raise IndexError
        self.current_pos['x'] = pos_x
        self.current_pos['y'] = pos_y

    def get_xy(self):
        """return current cursor position"""
        return self.current_pos

    def stream(self, string):
        """Stream string
        Args:
            string: string to display
        """
        raise NotImplementedError("stream not implemented")

    def is_twin(self):
        """returns true if we are using twin lcd"""
        return self.twin_lcd

    def get_line_address(self, pos_y=None):
        """Return start hex address for line
        Args:
            pos_y: line number
        """
        if pos_y is None:
            pos_y = self.current_pos['y']

        if pos_y >= self.height or pos_y < 0:
            raise IndexError

        if not self.is_twin() or pos_y < 2:
            return LCD_LINES[pos_y]

        return LCD_LINES[pos_y - 2]

    def _get_enable(self, pos_y=None):
        """get proper enable line
        Args:
            pos_y: line number
        """
        if pos_y is None:
            pos_y = self.current_pos['y']
        if self.is_twin() and pos_y > 1:
            enable = 1
        else:
            enable = 0

        return enable
