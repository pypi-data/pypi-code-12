#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=I0011,R0913,R0902,W0231
"""Main virtual lcd (vlcd) class"""

import charlcd.abstract.lcd as lcd

DISPLAY_MODE_DIRECT = 'direct'
DISPLAY_MODE_BUFFERED = 'buffered'


class CharLCDVirtual(lcd.CharLCD):
    """
    Virtual LCD class
    Shouldn't be instanced - use lcd_virtual_buffered or lcd_virtual_direct
    """

    def __init__(self, width, height, display_mode=DISPLAY_MODE_DIRECT):
        """init virtual display"""
        self.current_pos = {
            'x': 0,
            'y': 0
        }
        self.width = width
        self.height = height
        self.display_mode = display_mode
        self.displays = []
        self.active_display = None
        self.initialized = False

    def add_display(self, pos_x, pos_y, display, offset_x=0, offset_y=0):
        """add lcd to virtual display"""
        self.displays.append({
            'x': pos_x,
            'y': pos_y,
            'offset_x': offset_x,
            'offset_y': offset_y,
            'width': display.get_width(),
            'height': display.get_height(),
            'lcd': display
        })

    def get_displays(self):
        """return all displays"""
        return self.displays

    def get_display(self, pos_x, pos_y):
        """return display for (x,y) coords"""
        if pos_x > self.width or pos_x < 0 or pos_y > self.height or pos_y < 0:
            raise IndexError

        for display in self.displays:
            if display['x'] <= pos_x < display['x'] + display['width'] -\
               display['offset_x'] and \
               display['y'] <= pos_y < display['y'] + display['height'] -\
               display['offset_y']:
                    return display

        return None

    def init(self):
        """overwrite parent function"""
        pass

    def shutdown(self):
        """call shutdown on displays"""
        for display in self.displays:
            display.lcd.shutdown()

    def stream(self, string):
        """we inherit it so we should have some body"""
        lcd.CharLCD.stream(self, string)

    def write(self, string, pos_x=None, pos_y=None):
        """we inherit it so we should have some body"""
        lcd.CharLCD.write(self, string)
