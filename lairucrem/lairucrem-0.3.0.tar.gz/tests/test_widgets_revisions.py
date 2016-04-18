# -*- encoding: utf-8 -*-
#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""test lairucrem widgets"""

from __future__ import unicode_literals, absolute_import

from unittest import TestCase
from itertools import cycle
import sure
import urwid

from lairucrem.widgets import revisions


def test_line():
    widget = revisions._line('foo')
    widget.selectable().should.be.truthy
    'enter'.should.equal(widget.keypress((100,), 'enter'))


class test_walker(TestCase):
    def test_append_data(self):
        walker = revisions.walker([])

        walker.append_data('graph\0node\0content')
        (1).should.equal(len(walker))
        walker[0].selectable().should.be.truthy
        'graphcontent'.should.equal(walker[0].get_text()[0])

        walker.append_data('graph2')
        (2).should.equal(len(walker))
        walker[1].selectable().should.be.falsy
        'graph2'.should.equal(walker[1].get_text()[0])

    def test_get_next(self):
        walker = revisions.walker([])

        def fill_data(pos):
            if pos < 3:
                pos += 1
                walker.append_data('o\0%i\0desc%i' % (pos, pos))
                return True
            else:
                return False

        len(walker).should.be(0)
        urwid.connect_signal(walker, 'need_data', fill_data)

        walker.get_next(-1)
        len(walker).should.be(1)
        'odesc0'.should.equal(walker[0].get_text()[0])

        walker.get_next(-1)
        len(walker).should.be(1)
        'odesc0'.should.equal(walker[0].get_text()[0])

        walker.get_next(6)
        len(walker).should.be(1)

    def test_modified_callback(self):
        modified = []
        walker = revisions.walker([])
        walker.set_modified_callback(lambda: modified.append(True))

        def fill_data(pos):
            walker.append_data('o\0%i\0desc%i' % (pos, pos))
            return True

        urwid.connect_signal(walker, 'need_data', fill_data)
        walker.get_next(-1)
        modified.should.be.truthy


class test_listbox(TestCase):
    def test_render_seems_always_focused(self):
        was_focused = []
        class widget(urwid.Text):
            def render(self, size, focus):
                was_focused.append(focus)
                return super(widget, self).render(size, focus)

        listbox = revisions.listbox([widget('toto')])
        listbox.render((10, 10), False)
        [True].should.equal(was_focused)

    def test_keypress(self):
        signals = []
        listbox = revisions.listbox([])
        urwid.connect_signal(listbox, 'commandlist', lambda *a: signals.append('commandlist'))
        urwid.connect_signal(listbox, 'filter', lambda *a: signals.append('filter'))
        size = (10, 10)
        listbox.keypress(size, 'x')
        signals.should.be.falsy
        listbox.keypress(size, 'enter')
        'commandlist'.should.be.within(signals)
        listbox.keypress(size, '/')
        'filter'.should.be.within(signals)


def test_filterdialog():
    dialog = revisions.filterdialog('.^')
    dialog.get_revset().should.equal('.^')
    revsets = []
    closes = []
    urwid.connect_signal(dialog, 'filter', lambda w, r: revsets.append(r))
    urwid.connect_signal(dialog, 'close', lambda w: closes.append(True))

    size = (10, 10)

    dialog.keypress(size, ':')
    dialog.keypress(size, ':')
    dialog.keypress(size, 'enter')

    ['.^::'].should.equal(revsets)
    closes.should.be.falsy

    dialog.set_message('foo')
    'foo'.should.equal(dialog.message.get_text()[0])

    dialog.keypress(size, 'esc')
    closes.should.be.truthy
