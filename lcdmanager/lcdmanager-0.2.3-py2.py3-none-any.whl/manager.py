#!/usr/bin/python
# -*- coding: utf-8 -*-

"""LCD Manager"""
from builtins import object  # pylint: disable=I0011,W0622
import charlcd.abstract.lcd as lcd_abstract

TRANSPARENCY = ' '


class Manager(object):
    """Class Manager"""
    def __init__(self, lcd):
        if lcd.display_mode != lcd_abstract.DISPLAY_MODE_BUFFERED:
            raise AttributeError("lcd must be instance of buffered lcd")

        self.lcd = lcd
        self.widgets = []
        self.name_widget = {}
        self.size = {
            'width': self.lcd.get_width(),
            'height': self.lcd.get_height()
        }

    def flush(self):
        """display content"""
        self.lcd.flush()

    def render(self):
        """add widget view to lcd buffer"""
        for widget in self.widgets:
            if not widget.visibility:
                continue
            position = widget.position
            y_offset = 0
            for line in widget.render():
                if position['y'] + y_offset >= self.lcd.get_height():
                    break
                self.lcd.write(
                    line,
                    position['x'],
                    position['y'] + y_offset
                )
                y_offset += 1

    def add_widget(self, widget):
        """add widget to manager"""
        self.widgets.append(widget)
        if widget.name is not None:
            self.name_widget[widget.name] = len(self.widgets) - 1

    def get_widget(self, name):
        """get widget from  manager or None"""
        if name in self.name_widget:
            return self.widgets[self.name_widget[name]]

        return None

    @property
    def width(self):
        """manager width"""
        return self.size['width']

    @property
    def height(self):
        """manager height"""
        return self.size['height']
