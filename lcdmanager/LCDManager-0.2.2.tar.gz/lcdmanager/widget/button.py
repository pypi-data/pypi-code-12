#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Widget - label"""
from past.builtins import basestring  # pylint: disable=I0011,W0622
import lcdmanager.abstract.widget as widget
import lcdmanager.abstract.event.focus as focus
import lcdmanager.abstract.event.action as action

APPEND_MODE_OVERWRITE = 1


class Button(widget.Widget, focus.Focus, action.Action):
    """Label widget"""
    def __init__(self, pos_x, pos_y, name=None, visibility=True):
        self._label = {
            'base': [''],
            'display': [''],
            'pointer': {
                'before': '>',
                'after': '<',
                'append_mode': APPEND_MODE_OVERWRITE
            }
        }
        widget.Widget.__init__(self, pos_x, pos_y, name, visibility)
        focus.Focus.__init__(self)
        action.Action.__init__(self)

    @property
    def pointer_before(self):
        """return char for pointer before label"""
        return self._label['pointer']['before']

    @pointer_before.setter
    def pointer_before(self, char):
        """set char for pointer before label"""
        self._label['pointer']['before'] = char

    @property
    def pointer_after(self):
        """return char for pointer after label"""
        return self._label['pointer']['after']

    @pointer_after.setter
    def pointer_after(self, char):
        """set char for pointer after label"""
        self._label['pointer']['after'] = char

    @property
    def pointer_mode(self):
        """return char for pointer after label"""
        return self._label['pointer']['append_mode']

    @pointer_mode.setter
    def pointer_mode(self, mode):
        """set char for pointer after label"""
        self._label['pointer']['append_mode'] = mode

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
            self.width = self._calculate_width()
        if self.autoheight:
            self.height = len(self._label['base'])
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
        """prepare text to display by cropping it and append pointers"""
        rows = [label[0:self.width] for label in self._label['base']]
        if self._is_active():
            rows = [
                self._label['pointer']['before'] +
                label[
                    len(self._label['pointer']['before']):
                    ((len(self._label['pointer']['after']) * -1) or
                     len(label))
                ] +
                self._label['pointer']['after']
                for label in rows
            ]

        return rows[0: self.height]

    def event_focus(self):
        """gain focus"""
        self.has_focus = True
        self._label['display'] = self._crop_to_display()

    def event_blur(self):
        """lost focus"""
        self.has_focus = False
        self._label['display'] = self._crop_to_display()

    def event_action(self):
        """call action attached to widget"""
        return self.callback(self)  # pylint: disable=I0011,E1102

    def _is_active(self):
        if self.has_focus and \
           self._label['pointer']['append_mode'] == APPEND_MODE_OVERWRITE:
            return True
        return False
