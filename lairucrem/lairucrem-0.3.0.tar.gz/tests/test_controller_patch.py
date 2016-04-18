#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""test lairucrem controller."""

from __future__ import unicode_literals, absolute_import

from unittest import TestCase
import sure

import os
import io
import urwid
import re
import sh
from lairucrem import controller, widgets
from .test_utils import temprepo, mock, mockloop


def test_load_patch_description():
    ctrl = controller._patchcontroller(sh.gh)

    # cwd
    co = ctrl._load_patch_description(None)
    proc = co.send(None)
    'summary'.should.be.within(unicode(proc))
    co.send('\n')
    co.send('hello\nworld!')
    'hello'.should.be.within(''.join(ctrl.widget.render((20, 20)).text))

    # cwd
    co = ctrl._load_patch_description('myhash')
    proc = co.send(None)
    'log'.should.be.within(unicode(proc))


def test_load_patch_stat():
    ctrl = controller._patchcontroller(sh.gh)

    # cwd
    co = ctrl._load_patch_stats(None)
    proc = co.send(None)
    'diff'.should.be.within(unicode(proc))
    '--stat'.should.be.within(unicode(proc))
    co.send('\n')
    co.send(' filepath.py |  4 +-')
    co.send('otherfilepath.py |  4 +-')
    'filepath.py'.should.be.within(''.join(ctrl.widget.render((20, 20)).text))

    # cwd
    co = ctrl._load_patch_stats('myhash')
    proc = co.send(None)
    'log'.should.be.within(unicode(proc))
    '--stat'.should.be.within(unicode(proc))
    '--template= '.should.be.within(unicode(proc))


def test_load_patch_diff():
    ctrl = controller._patchcontroller(sh.gh)

    co = ctrl._load_patch_stats(None)
    co.send(None)
    co.send('\n')
    co.send(' filepath.py |  4 +-')

    co = ctrl._load_patch_diff('myhash', 'filepath.py', ctrl._tree._children[-1])
    proc = co.send(None)
    'diff'.should.be.within(unicode(proc))
    'filepath.py'.should.be.within(unicode(proc))
    co.send('\n')
    co.send('@@ 1,1 2,1 @@')
    co.send('hello')
    ctrl._tree.expand(recursive=True)
    '@@ 1,1 2,1 @@'.should.be.within(''.join(ctrl.widget.render((20, 20)).text))


def test_workflow():
    with temprepo() as repo:
        node = repo.mkcset('foo', 'description\nmultiline desc', user='myself').__unicode__().strip()

        os.remove(os.path.join(repo._root, 'foo'))
        with io.open(os.path.join(repo._root, 'bar'), 'w', encoding='utf8') as fid:
            fid.write('babar')

        ctrl = controller._patchcontroller(repo)
        def monitor_sh(co, *a, **k):
            proc = next(co)
            for line in proc():
                co.send(line)
        urwid.connect_signal(ctrl, 'monitor_sh', monitor_sh)

        ctrl.refresh()
        ctrl._tree.expand(recursive=True)
        results = ' '.join(ctrl.widget.render((20, 20)).text)
        '1 deleted'.should.be.within(results)
        '1 unknown'.should.be.within(results)

        ctrl.refresh(node)
        ctrl._tree.expand(recursive=True)
        results = ' '.join(ctrl.widget.render((20, 20)).text)
        'multiline desc'.should.be.within(results)


def test_search():
    with temprepo() as repo:
        for i in range(2):
            cset = unicode(repo.mkcset('foo', 'cset %i' % i))
        ctrl = controller._patchcontroller(repo)
        ctrl._create_process(cset)

        dialog = []
        ctrl.connect('open_popup', lambda d: dialog.append(d))

        ctrl._search()
        dialog.should.be.truthy

        diag = dialog[0]
        diag._emit('search', re.compile('cset'))

        ctrl.widget.render((200, 200))
        ctrl._tree.search_pattern.should.be.truthy
