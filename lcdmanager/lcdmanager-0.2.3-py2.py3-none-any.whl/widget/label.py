#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Widget - label"""
from past.builtins import basestring  # pylint: disable=I0011,W0622
import lcdmanager.abstract.widget as widget


class Label(widget.Widget):
    """Label widget"""

    def __init__(self, pos_x, pos_y, name=None, visibility=True):
        self._label = {
            'base': [''],
            'display': ['']
        }
        widget.Widget.__init__(self, pos_x, pos_y, name, visibility)

    @property
    def label(self):
        """return label text"""
        return self._label['base']

    @label.setter
    def label(self, label):
        """set label"""
        if isinstance(label, basestring):
            self._label['base'] = [label]
        else:
            self._label['base'] = label
        if self.autowidth:
            self._size['width'] = self._calculate_width()

        if self.autoheight:
            self._size['height'] = len(self._label['base'])
        self._label['display'] = self._crop_to_display()

    def render(self):
        """return view array"""
        return self._label['display']

    @widget.Widget.width.setter  # pylint: disable=I0011,E1101
    def width(self, width):  # pylint: disable=I0011,W0221
        """set width"""
        widget.Widget.width.fset(self, width)  # pylint: disable=I0011,E1101
        self._label['display'] = self._crop_to_display()

    @widget.Widget.autowidth.setter  # pylint: disable=I0011,E1101
    def autowidth(self, enabled):  # pylint: disable=I0011,W0221
        """set autowidth"""
        widget.Widget.autowidth.fset(  # pylint: disable=I0011,E1101
            self,
            enabled
        )
        if enabled:
            self.label = self._label['base']

    @widget.Widget.height.setter  # pylint: disable=I0011,E1101
    def height(self, height):  # pylint: disable=I0011,W0221
        """set width"""
        widget.Widget.height.fset(self, height)  # pylint: disable=I0011,E1101
        self._label['display'] = self._crop_to_display()

    @widget.Widget.autoheight.setter  # pylint: disable=I0011,E1101
    def autoheight(self, enabled):  # pylint: disable=I0011,W0221
        """set autowidth"""
        widget.Widget.autoheight.fset(  # pylint: disable=I0011,E1101
            self,
            enabled
        )
        if enabled:
            self.label = self._label['base']

    def _calculate_width(self):
        """calculate longest row in dictionary"""
        return max(len(label) for label in self._label['base'])

    def _crop_to_display(self):
        """prepare text to display by cropping it"""
        rows = [label[0:self.width] for label in self._label['base']]
        return rows[0: self.height]
