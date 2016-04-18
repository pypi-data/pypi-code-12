# -*- encoding: utf-8 -*-
#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""test lairucrem widgets"""

from __future__ import unicode_literals, absolute_import

from unittest import TestCase
import sure

import itertools
import urwid

from lairucrem import widgets
from lairucrem.widgets import revisions
from . import test_utils


class test_revisions(TestCase):
    def test_append_data(self):
        revs = revisions.walker([])
        len(revs).must.equal(0)
        # full line
        revs.append_data('  #  \0a1236ef\0desc\0ad ')
        len(revs).must.equal(1)
        # graph only
        revs.append_data('/ | \\')
        len(revs).must.equal(2)
        # Test displayed content ok
        revisions.listbox(revs).render((13, 2)).text.must.equal([
            '  #  desc\0ad ',
            '/ | \\        ',
        ])

    def test_type_of_items(self):
        revs = revisions.walker([])
        # full line
        revs.append_data('  #  \0a1236ef\0desc\0ad ')
        revs[-1].selectable().must.be.truthy
        # graph only
        revs.append_data('/ | \\')
        revs[-1].selectable().must.be.falsy


class test_choices(TestCase):
    def setUp(self):
        self.widget = widgets.choices(['first', 'second', 'third'])

    def test_click_choice(self):
        response = []
        urwid.connect_signal(self.widget, 'selected', lambda x, i: response.append(i))
        self.widget.keypress((10, 10), 'down')
        self.widget.keypress((10, 10), 'down')
        self.widget.keypress((10, 10), 'enter')
        response.should.equal([1])

    def test_click_close(self):
        response = []
        urwid.connect_signal(self.widget, 'close', lambda x: response.append(x))
        self.widget.keypress((10, 10), 'down')
        self.widget.keypress((10, 10), 'down')
        self.widget.keypress((10, 10), 'down')
        self.widget.keypress((10, 10), 'enter')
        response.should.be.truthy

    def test_hit_choice(self):
        response = []
        urwid.connect_signal(self.widget, 'selected', lambda x, i: response.append(i))
        self.widget.keypress((10, 10), 'b')
        response.should.equal([1])

    def test_hit_close(self):
        response = []
        urwid.connect_signal(self.widget, 'close', lambda x: response.append(x))
        self.widget.keypress((10, 10), 'esc')
        response.should.truthy

class test_multiplechoices(TestCase):
    def setUp(self):
        self.widget = widgets.multiplechoices(
            ['first', 'second', 'third'],
            (('action1', 'a', 'help for action1'),
             ('action2', 'b', 'help for action2'))
        )

    def test_click_choice(self):
        response = []
        urwid.connect_signal(self.widget, 'selected', lambda x, i: response.append(i))
        self.widget.keypress((10, 10), 'down')
        self.widget.keypress((10, 10), 'down')
        self.widget.keypress((10, 10), 'enter')
        self.widget.keypress((10, 10), 'down')
        self.widget.keypress((10, 10), 'enter')
        self.widget._apply('action1')
        response.should.equal([('action1', [1, 2])])

    def test_action_key(self):
        response = []
        urwid.connect_signal(self.widget, 'selected', lambda x, i: response.append(i))
        self.widget.keypress((10, 10), 'a')
        response.should.equal([('action1', [])])

    def test_action_help(self):
        self.widget.keypress((10, 10), 'right')
        self.widget.message.get_text()[0].should.equal('help for action1')
