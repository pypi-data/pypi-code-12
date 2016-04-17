#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Widget - canvas"""
from builtins import range  # pylint: disable=I0011,W0622
import lcdmanager.abstract.widget as widget


class Canvas(widget.Widget):
    """Canvas widget"""
    def __init__(self, pos_x, pos_y, width, height,
                 name=None, visibility=True):
        widget.Widget.__init__(self, pos_x, pos_y, name, visibility)
        self.width = width
        self.height = height
        self.screen = []
        self.clear()
        self.cursor_position = {
            'x': 0,
            'y': 0
        }

    def clear(self):
        """clear screen"""
        self.screen = [" ".ljust(self.width, " ")
                       for _ in range(0, self.height)]

    def render(self):
        """return view array"""
        return self.screen

    @property
    def x(self):
        """get x cursor position"""
        return self.cursor_position['x']

    @x.setter
    def x(self, value):
        """set x cursor position"""
        self.cursor_position['x'] = value

    @property
    def y(self):
        """get y cursor position"""
        return self.cursor_position['y']

    @y.setter
    def y(self, value):
        """set y cursor position"""
        self.cursor_position['y'] = value

    def write(self, string, pos_x=None, pos_y=None):
        """writes a string"""
        if pos_x is None:
            pos_x = self.cursor_position['x']
        else:
            self.cursor_position['x'] = pos_x
        if pos_y is None:
            pos_y = self.cursor_position['y']

        if pos_x < self.width and pos_y < self.height:
            line = self.screen[pos_y]
            new_line = line[0:pos_x] + string + line[pos_x + len(string):]
            line = new_line[:self.width]
            self.screen[pos_y] = line
            self._inc_c(len(string))
        else:
            if pos_x > self.width:
                self.x = self.width
            if pos_y > self.height:
                self.y = self.height

    def _inc_c(self, length):
        """move a cursor by length"""
        self.x += length
        if self.x > self.width:
            self.x = self.width
