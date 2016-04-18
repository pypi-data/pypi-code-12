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
import time
import urwid
import re
from lairucrem import controller, widgets
from .test_utils import temprepo, mock, mockloop


class test_controller(TestCase):

    def test_patch_content_updated(self):
        with temprepo() as hg:
            for i in range(3):
                hg.mkcset('cset%i' % i, 'cset%i' % i)
            newpath = os.path.join(hg._root, 'cset3')
            with io.open(newpath, 'w', encoding='utf8') as fid:
                fid.write('draft')
            hg.add(newpath)

            ml = mockloop([])
            ctrl = controller.controller(hg, template='{rev} {desc}', revset=None, mainloop=ml)

            ml.widget.should.be(ctrl.widget)

            ctrl.refresh()

            revisions = ctrl._revisions_ctrl
            patch = ctrl._patch_ctrl
            size = (50, 50)

            ml.loop(True)
            time.sleep(0.1)
            ml.loop(True)

            # # initial commit selected (working)
            'cset3'.must.be.within('\n'.join(patch.widget.render(size).text))
            # others
            revisions._walker.get_next(10) # load data
            revisions._walker.set_focus(2)

            # expand diff
            patch._tree.expand(recursive=True) # force loading data
            time.sleep(0.1)
            ml.loop(True)

            'cset2'.must.be.within('\n'.join(patch.widget.render(size).text))

            # patch retrieved on focus
            revisions._walker.set_focus(6)
            time.sleep(0.5)
            ml.loop(True)
            'cset0'.must.be.within('\n'.join(patch.widget.render(size).text))

    def test_refresh(self):
        with temprepo() as repo:
            for i in range(10):
                repo.mkcset('foo', 'cset %i' % i)
            ml = mockloop([])
            ctrl = controller.controller(repo, template='{rev} {desc}', revset=None, mainloop=ml)
            ctrl.refresh()
            revisions = ctrl._revisions_ctrl._walker
            revisions.get_next(100) # load all
            len(revisions).must.equal(22)
            for i in range(2):
                repo.mkcset('foo', 'cset %i' % i)
            revisions.get_next(100) # load all
            len(revisions).must.equal(22)
            ctrl.refresh()
            revisions.get_next(100) # load all
            len(revisions).must.equal(26)

    def test_run_interactive_command(self):
        with temprepo() as repo:
            ml = mockloop([])
            ctrl = controller.controller(repo, template='{rev} {desc}', revset=None, mainloop=ml)
            run = []
            def cmds():
                run.append('foo')
                yield 'foo'
                run.append('bar')
                yield 'bar'
                run.append('end')
            ctrl._revisions_ctrl._proc.should.be.falsy
            cmd = cmds()
            cmd.send(None)
            ctrl._run_interactive_command(cmd)
            ['foo', 'bar', 'end'].should.equal(run)
            ctrl._revisions_ctrl._proc.should.be.truthy # refresh don

    def test_run_interactive_command_with_dialog(self):
        with temprepo() as repo:
            ml = mockloop([])
            ctrl = controller.controller(repo, template='{rev} {desc}', revset=None, mainloop=ml)
            run = []
            dialog = widgets.simpledialog(urwid.Text('toto'), 'toto')
            def cmds():
                yield True
                continuator = yield dialog
                run.append('foo')
                yield 'foo'
                run.append('bar')
                yield 'bar'
                run.append('end')
            ctrl._revisions_ctrl._proc.should.be.falsy
            cmd = cmds()
            cmd.send(None)
            cor = ctrl._run_interactive_command(cmd)
            ctrl.widget._pop_up_widgets.should.be.truthy
            run.should.be.falsy
            dialog._emit('close')
            ['foo', 'bar', 'end'].should.equal(run)
            ctrl._revisions_ctrl._proc.should.be.truthy # refresh don
        
    def test_open_popup(self):
        ctrl = controller.controller(None, template='{rev} {desc}', revset=None)
        dialog = widgets.simpledialog(urwid.Text(''), 'dialog')
        ctrl._open_popup(dialog)
        ctrl.widget._pop_up_widgets[-1].should.be(dialog)
        # open another one
        dialog2 = urwid.Text('')
        ctrl._open_popup(dialog2)
        ctrl.widget._pop_up_widgets[0].should.be(dialog)
        ctrl.widget._pop_up_widgets[-1].should.be(dialog2)
        # close the first ont
        urwid.emit_signal(dialog, 'close')
        ctrl.widget._pop_up_widgets[0].should.be(dialog2)
        len(ctrl.widget._pop_up_widgets).should.equal(1)
        

    def test_redraw(self):
        ml = mockloop(None)
        ctrl = controller.controller(None, template='{rev} {desc}', revset=None, mainloop=ml)
        ctrl._redraw()
        fdrd = ml._watch_pipes[ml._force_redraw_pipe][0]
        os.read(fdrd, 1).should.be.truthy
