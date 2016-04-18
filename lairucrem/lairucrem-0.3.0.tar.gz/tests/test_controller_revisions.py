#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""test lairucrem controller."""

from __future__ import unicode_literals, absolute_import

from unittest import TestCase
import sure

import urwid
from lairucrem import controller
from .test_utils import temprepo


class test_revisionscontroller(TestCase):
    def test_revisionscontroller(self):
        with temprepo() as hg:
            for i in range(11):
                hg.mkcset('foo', 'cset %i' % i)
            ctrl = controller._revisionscontroller(hg, template='{desc}', revset='desc("cset 1")')
            ctrl.refresh()
            ctrl._fill_widget(10)
            sum(1 for w in ctrl._walker if w.selectable()).must.equal(3) # working, 1 and 10

    def test_incremental_load_in_tree(self):
        with temprepo() as hg:
            for i in range(5):
                hg.mkcset('foo', 'cset %i' % i)
            ctrl = controller._revisionscontroller(hg, template='{rev} {desc}', revset=None)
            ctrl.refresh()
            revisions = ctrl._walker
            ctrl.widget.render((20, 2))
            len(revisions).must.equal(2)
            ctrl.widget.render((20, 4))
            len(revisions).must.equal(4)
            ctrl.widget.render((20, 20))
            len(revisions).must.be.lower_than(20)

    def test_command_list(self):
        with temprepo() as hg:
            for i in range(5):
                cset = unicode(hg.mkcset('foo', 'cset %i' % i))
            ctrl = controller._revisionscontroller(hg, template='{rev} {desc}', revset=None)
            ctrl.refresh()
            ctrl._node = cset
            dialog = []
            commands = []
            ctrl.connect('open_popup', dialog.append)
            ctrl.connect('run_commands', lambda cmds: commands.append(cmds))
            ctrl._command_list()
            dialog.should.be.truthy

            diag = dialog[0]
            diag._emit('selected', 0)

            commands.should.be.truthy

    def test_filter_ok(self):
        with temprepo() as hg:
            for i in range(2):
                cset = unicode(hg.mkcset('foo', 'cset %i' % i))
            ctrl = controller._revisionscontroller(hg, template='{rev} {desc}', revset=None)
            dialog = ctrl._ask_revset()
            closed = []
            urwid.connect_signal(dialog, 'close', lambda: closed.append(True))
            dialog._emit('filter', 'desc(cset1)')
            (1).should.equal(len(ctrl._walker))
            closed.should.be.truthy

    def test_filter_nok(self):
        with temprepo() as hg:
            for i in range(2):
                cset = unicode(hg.mkcset('foo', 'cset %i' % i))
            ctrl = controller._revisionscontroller(hg, template='{rev} {desc}', revset='foo')
            dialog = ctrl._ask_revset()
            dialog.get_revset().should.equal('foo')
            dialog._emit('filter', 'desc(')
            'error'.should.be.within(dialog.message.get_text()[0])

