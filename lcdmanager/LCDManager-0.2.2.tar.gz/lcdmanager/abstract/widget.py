#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Widget - abstract class"""
from builtins import object  # pylint: disable=I0011,W0622


class Widget(object):
    """Widget abstract class"""
    def __init__(self, pos_x, pos_y, name=None, visibility=True):
        self._position = {}
        self._visibility = False
        self.position = {
            'x': pos_x,
            'y': pos_y
        }
        self.name = name
        self.visibility = visibility
        self._size = {
            'width': 0,
            'autowidth': True,
            'height': 0,
            'autoheight': True
        }

    def render(self):
        """returns widget view array"""
        raise NotImplementedError("render not implemented")

    @property
    def position(self):
        """returns widget position"""
        return self._position

    @position.setter
    def position(self, pos):
        """sets widget position"""
        if not isinstance(pos, dict):
            raise AttributeError("dict with x and y required")
        if 'x' not in pos or 'y' not in pos:
            raise AttributeError("x and y required")
        self._position = pos

    @property
    def visibility(self):
        """return widget visibility"""
        return self._visibility

    @visibility.setter
    def visibility(self, visibility):
        """sets widget visibility"""
        if not isinstance(visibility, bool):
            raise AttributeError("Boolean required")
        self._visibility = visibility

    @property
    def width(self):
        """get width"""
        return self._size['width']

    @width.setter
    def width(self, width):
        """set width"""
        self._size['width'] = width
        self._size['autowidth'] = False

    @property
    def autowidth(self):
        """get autowidth"""
        return self._size['autowidth']

    @autowidth.setter
    def autowidth(self, enabled):
        """set autowidth"""
        self._size['autowidth'] = enabled

    @property
    def height(self):
        """get width"""
        return self._size['height']

    @height.setter
    def height(self, height):
        """set width"""
        self._size['height'] = height
        self._size['autoheight'] = False

    @property
    def autoheight(self):
        """get autowidth"""
        return self._size['autoheight']

    @autoheight.setter
    def autoheight(self, enabled):
        """set autowidth"""
        self._size['autoheight'] = enabled
