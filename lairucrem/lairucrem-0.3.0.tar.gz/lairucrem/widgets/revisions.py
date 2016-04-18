# -*- encoding: utf-8 -*-
#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""Main UI widgets for revision tree."""

from __future__ import unicode_literals, absolute_import

import urwid

from . import lightbutton


class _line(urwid.Text):
    """a simple selectable Text"""
    _selectable = True
    #pylint: disable=unused-argument
    @staticmethod
    def keypress(size, key):
        """return key"""
        return key


class walker(urwid.SimpleFocusListWalker):
    """A widgets container that loads data on demand."""

    signals = ['need_data']

    def append_data(self, data):
        """Append new changeset data. """
        data = data.rstrip()
        if '\0' in data: # more than graph chars
            graph, node, content = data.split('\0', 2)
            widget = urwid.AttrWrap(_line(graph + content, wrap=urwid.CLIP), None, 'focus')
            widget.node = node
        else:
            widget = urwid.Text(data) #pylint: disable=redefined-variable-type
        self.append(widget)

    def get_next(self, pos):
        """return (widget, position) after the given position."""
        widget, position = super(walker, self).get_next(pos)
        if position is not None:
            return widget, position
        urwid.emit_signal(self, 'need_data', pos)
        return super(walker, self).get_next(pos)

    def set_modified_callback(self, callback):
        """Assign a callback function with no parameters that is called any
        time the list is modified.  Callback's return value is ignored.
        """
        self._modified = callback


class listbox(urwid.ListBox):
    """ListBox that is always focused. This is useful to keep current
    selection highlighted"""
    signals = ['commandlist', 'filter']

    #parent is a delegator
    #pylint: disable=signature-differs
    #pylint: disable=method-hidden
    def render(self, size, focus):
        """render widget"""
        return super(listbox, self).render(size, True)

    def keypress(self, size, key):
        """process keypress"""
        if key == 'enter':
            self._emit('commandlist')
            return
        elif key == '/':
            self._emit('filter')
            return
        else:
            return super(listbox, self).keypress(size, key)


class filterdialog(urwid.WidgetWrap):
    """dialog to ask for a revset"""

    signals = ['close', 'filter']

    def __init__(self, revset=''):
        self.setup_ui(revset)
        urwid.connect_signal(self.closer, 'click', lambda button: self._cancel())
        urwid.connect_signal(self.applier, 'click', lambda button: self._search())
        #pylint: disable=not-callable
        super(filterdialog, self).__init__(urwid.AttrWrap(self.fill, 'highlight'))

    @staticmethod
    def get_rows():
        """prefered height"""
        return 10

    def setup_ui(self, revset):
        """build the widgets"""
        self.closer = lightbutton("[esc] Cancel")
        self.applier = lightbutton("[enter] Filter")
        self.edit = urwid.Edit('', edit_text=revset or '')
        self.message = urwid.Text('')
        pile = urwid.Pile([
            urwid.Divider(),
            urwid.Text('Revision set expression:'),
            urwid.AttrWrap(self.edit, 'button', 'button_hover'),
            urwid.Divider(),
            urwid.Padding(urwid.Columns([
                ('fixed', 18, urwid.AttrWrap(self.applier, 'button', 'button_hover')),
                ('fixed', 16, urwid.AttrWrap(self.closer, 'button', 'button_hover')),
            ], dividechars=2), align=urwid.CENTER, width=50),
            self.message,
        ])
        self.fill = urwid.LineBox(urwid.Filler(pile, min_height=20),
                                  tline='━', bline='━',
                                  lline='┃', rline='┃',
                                  title='Select a set of revisions')

    #pylint: disable=unused-argument
    def _search(self, *args):
        """send signal to apply the revset."""
        pattern = self.get_revset()
        self.set_message('Selecting the set of revision...')
        self._emit('filter', pattern)

    def get_revset(self):
        """return the revset"""
        return self.edit.edit_text

    def set_message(self, msg):
        """set a message for the user"""
        self.message.set_text(msg)

    #pylint: disable=unused-argument
    def _cancel(self, *args):
        """send signals to revert back the revset and to close the popup."""
        self._emit('close')

    def keypress(self, size, key):
        """process keypress"""
        if key == 'esc':
            self._cancel()
            return
        if key == 'enter':
            self._search()
        #pylint: disable=not-callable
        return super(filterdialog, self).keypress(size, key)
