# -*- encoding: utf-8 -*-
#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""UI widgets for lairucrem."""

from __future__ import unicode_literals, absolute_import

from string import ascii_letters
import urwid


class lightbutton(urwid.Button):
    """Simple button without decoration"""
    button_left = urwid.Text("")
    button_right = urwid.Text("")


class text(urwid.Text):
    """Same as urwid.Text but provide a 'hightlight(pattern)' method to
    highlight content"""

    def __init__(self, *args, **kwargs):
        self._default_style = kwargs.pop('default_style', 'default')
        self._search_pattern_getter = kwargs.pop('search_pattern_getter')
        super(text, self).__init__(*args, **kwargs)

    def get_text(self):
        """return text, attrib"""
        # called only when widget is invalidated
        pattern = self._search_pattern_getter()
        if not pattern:
            # that's urwid fault :P
            #pylint: disable=attribute-defined-outside-init
            self._attrib = [(self._default_style, len(self._text))]
            return self._text, self._attrib

        default_style = self._default_style
        prev_end = 0
        styles = []
        for match in pattern.finditer(self._text):
            start = match.start()
            end = match.end()
            prev_length = start - prev_end
            if prev_length:
                styles.append((default_style, prev_length))
            length = match.end() - match.start()
            styles.append(('match', length))
            prev_end = end
        if prev_end < len(self._text):
            styles.append((default_style, len(self._text) - prev_end))
        self._attrib[:] = styles
        return self._text, self._attrib


class simpledialog(urwid.WidgetWrap):
    """A simple dialog box that displays a content widget."""
    signals = ['close']
    close = 'after'

    def __init__(self, content, title):
        self._content = content
        super(simpledialog, self).__init__(
            urwid.AttrWrap(self.setup_ui(content, title), 'highlight'))

    def _build_buttons(self):
        """build the dialog buttons"""
        closer = lightbutton("[esc] Cancel")
        urwid.connect_signal(closer, 'click', lambda button: self._cancel())
        return [closer]

    def get_rows(self):
        """Return the prefered height of the dialog"""
        if getattr(self._content, 'get_rows', None):
            return self._content.get_rows() + 5
        return 10

    def _setup_ui(self, content):
        """Setup the inner widget"""
        return urwid.Pile([
            content,
            urwid.Divider(),
            urwid.Padding(urwid.Columns([
                urwid.AttrWrap(button, 'button', 'button_hover')
                for button in self._build_buttons()
            ], dividechars=2), align=urwid.CENTER, width=50),
        ])

    def setup_ui(self, content, title):
        """Setup widgets"""
        return urwid.LineBox(urwid.Filler(self._setup_ui(content), min_height=20),
                             tline='━', bline='━',
                             lline='┃', rline='┃',
                             title=title)

    #pylint: disable=unused-argument
    def _cancel(self, *args):
        """send signals to revert back the revset and to close the popup."""
        self._emit('close')

    def keypress(self, size, key):
        """process keypress"""
        if key == 'esc':
            self._cancel()
            return
        #pylint sucks
        #pylint: disable=not-callable
        return super(simpledialog, self).keypress(size, key)


class choices(simpledialog):
    """A dialog that allows users to choose from a list of choices.

    Choices are displayed in a widget with buttons. User can select a
    choice by clickin a button or by hitting an associated key
    shortcut (a letter linked automatically). No more that
    `len(shortcuts)` choices is allowed.

    Signals
    -------

    :selected: fired when the user selects a choice. The choice index
               is given as callback parameter.

    :close: fired when the user cancels the selection with no selected
            choice.
    """

    signals = ['selected']
    shortcuts = ascii_letters + r'1234567890~!@#$%^&*()_+,./[]\<>?{}|;:'
    def __init__(self, choicelist):
        self.choices = choicelist
        super(choices, self).__init__(
            urwid.AttrWrap(self._setup_content(), 'highlight'), 'choices')

    def get_rows(self):
        """Return the prefered height for the dialog"""
        return len(self.choices) * 2 + 5

    def _setup_content(self):
        """set up widgets"""
        _choices = [urwid.AttrWrap(
            lightbutton('[%s] %s' % (l, choice), on_press=lambda b, c=i: self._select(c)),
            'button', 'button_hover'
        ) for i, (l, choice) in enumerate(zip(self.shortcuts, self.choices))]
        if _choices:
            message = 'The following action(s) can be applied to the selected changeset:'
        else:
            message = 'No proper choice found'
        return urwid.Pile([
            urwid.Divider(),
            urwid.Text(message)
        ] + _choices)

    def _setup_ui(self, content):
        return urwid.Pile([
            urwid.Padding(urwid.Columns([
                urwid.AttrWrap(button, 'button', 'button_hover')
                for button in self._build_buttons()
            ], dividechars=2), align=urwid.CENTER, width=50),
            content,
            urwid.Divider(),
        ])

    def _select(self, choice):
        """send signal to apply the revset."""
        self._emit('selected', choice)
        self._emit('close')

    def _cancel(self):
        """send signals to revert back the revset and to close the popup."""
        self._emit('close')

    def keypress(self, size, key):
        """pocess key press"""
        #pylint sucks
        #pylint: disable=not-callable
        key = super(choices, self).keypress(size, key)
        if not key:
            return
        if key == 'esc':
            self._cancel()
            return
        elif key in self.shortcuts:
            index = self.shortcuts.find(key)
            if len(self.choices) > index:
                self._select(index)
                return
        return key


class multiplechoices(simpledialog):
    """A dialog box to select multiple items from a list.

    signals:

    - close: provides the widget to the callback
    - apply: provides the widget to the callback and the list of selected choice indexes
    """
    signals = ['selected']
    shortcuts = ascii_letters + r'1234567890~!@#$%^&*()_+,./[]\<>?{}|;:'
    def __init__(self, choicelist, actions=(('apply', 'meta enter', 'apply action'),)):
        self.choices = choicelist
        self.actions = actions
        self._action_keys, self._action_descs = zip(*((key, desc) for dummy, key, desc in actions))
        self.message = urwid.Text('')
        self._checkboxes = []
        super(multiplechoices, self).__init__(
            urwid.AttrWrap(self._setup_content(), 'highlight'), 'choices')

    def get_rows(self):
        """Return the prefered height for the dialog"""
        return len(self.choices)*2 + 6

    def _on_focus_changed(self, widget, focus):
        """Set the help message when focusing on another action."""
        self.message.set_text(self._action_descs[focus])
        self._invalidate()
        widget._invalidate()

    def _build_buttons(self):
        """build the dialog buttons"""
        closer = lightbutton("[esc] Cancel")
        urwid.connect_signal(closer, 'click', lambda button: self._cancel())
        buttons = [closer]
        self._action_descs = ('close the dialog', ) + self._action_descs
        for action, key, dummy in self.actions:
            if key:
                txt = "[%s] %s" % (key, action)
            else:
                txt = action
            button = lightbutton(txt)
            urwid.connect_signal(button, 'click',
                                 lambda button, action=action: self._apply(action))
            buttons.append(button)
        return buttons

    def _build_buttons_wrapper(self):
        """build buttons with wrapper that display the corresponding help messages"""
        buttons = urwid.Columns([
            urwid.AttrWrap(button, 'button', 'button_hover')
            for button in self._build_buttons()
        ], dividechars=2)
        #pylint: disable=protected-access
        buttons._contents.set_focus_changed_callback(lambda f: self._on_focus_changed(buttons, f))
        return buttons

    def _setup_content(self):
        """set up widgets"""
        self._checkboxes = [urwid.AttrWrap(
            urwid.CheckBox('%s' % choice, user_data=1),
            'button', 'button_hover'
        ) for choice in self.choices]
        if self._checkboxes:
            message = 'Select entries:'
        else:
            message = 'No proper choice found'
        return urwid.Pile([
            urwid.Divider(),
            urwid.Text(message)
        ] + self._checkboxes)

    def _setup_ui(self, content):
        """setup inner widgets"""
        wrapper = urwid.Pile([urwid.Padding(self._build_buttons_wrapper(), align=urwid.CENTER),
                              content, urwid.Divider(), self.message])
        return wrapper

    def _apply(self, action):
        """send signal to apply the revset."""
        indices = [i for i, checkbox in enumerate(self._checkboxes) if checkbox.state]
        self._emit('selected', (action, indices))
        self._emit('close')

    def _cancel(self):
        """send signals to revert back the revset and to close the popup."""
        self._emit('close')

    def keypress(self, size, key):
        """pocess key press"""
        #pylint sucks
        #pylint: disable=not-callable
        key = super(multiplechoices, self).keypress(size, key)
        if not key:
            return
        if key == 'esc':
            self._cancel()
            return
        elif key in self._action_keys:
            self._apply(self.actions[self._action_keys.index(key)][0])
            return
        return key
