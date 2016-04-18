# -*- encoding: utf-8 -*-
#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""Test for lairucrem.widgets.mainwidget."""

from __future__ import unicode_literals, absolute_import

from unittest import TestCase
import sure

import urwid
from urwid.widget import delegate_to_widget_mixin

from lairucrem.widgets import mainwidget


class test_popuplauncher(TestCase):
    def test_simple_popup_widget(self):
        content = urwid.Filler(urwid.Text('==============='))
        widget = mainwidget.popuplauncher(content)

        size = (6, 15)

        # nothing by default
        canva = widget.render(size)
        canva.get_pop_up().should.be.falsy
        
        popup = urwid.Filler(urwid.Text('Hello\nworld!'))
        widget.open_pop_up(popup)
        canva = widget.render(size)
        (left, top, (widget, height, width)) = canva.get_pop_up()
        (2).should.equal(left)
        (2).should.equal(top)
        (2).should.equal(height)
        (11).should.equal(width)
        widget.should.be(popup)

    def test_dialog_popup(self):
        
        class dialog(delegate_to_widget_mixin('body')):
            """dialog box"""
            signals = ['close']
            def __init__(self):
                self.body = urwid.Filler(urwid.Text('popup'))
            def keypress(self, size, key):
                if key == 'q':
                    self._emit('close')
                return
            def get_rows(self):
                return 7
        content = urwid.Filler(urwid.Text('==============='))
        widget = mainwidget.popuplauncher(content)

        # test simple dialog
        popup = dialog()
        widget.open_pop_up(popup)
        size = (15, 15)
        canva = widget.render(size)
        canva.get_pop_up().should.be.truthy
        (left, top, (widget, width, height)) = canva.get_pop_up()
        (7).should.equal(height)
        (4).should.equal(top)

        popup.keypress(size, 'q')
        canva = widget.render(size)
        canva.get_pop_up().should.be.falsy
        

class test_packer(TestCase):
    def test_orientation(self):
        widgets = [urwid.Filler(urwid.Text('hello')), urwid.Filler(urwid.Text('world'))]
        packer = mainwidget.packer(widgets)

        size = (200, 60)
        packer.render(size)
        'horizontal'.should.equal(packer._orientation)
        isinstance(packer._original_widget, urwid.Columns).should.be.truthy

        size = (60, 200)
        packer.render(size)
        'vertical'.should.equal(packer._orientation)
        isinstance(packer._original_widget, urwid.Pile).should.be.truthy

    def test_keypress(self):
        widgets = [urwid.Filler(urwid.SelectableIcon('hello')),
                   urwid.Filler(urwid.SelectableIcon('world'))]
        packer = mainwidget.packer(widgets)

        size = (200, 60)
        packer.render(size)
        packer._original_widget.focus_position.should.be.equal(0)

        packer.keypress(size, None)
        packer._original_widget.focus_position.should.be.equal(0)

        packer.keypress(size, 'right')
        packer._original_widget.focus_position.should.be.equal(1)        
        packer.keypress(size, 'right')
        packer._original_widget.focus_position.should.be.equal(1)

        packer.keypress(size, 'left')
        packer._original_widget.focus_position.should.be.equal(0)
        packer.keypress(size, 'left')
        packer._original_widget.focus_position.should.be.equal(0)

        packer.keypress(size, 'tab')
        packer._original_widget.focus_position.should.be.equal(1)
        packer.keypress(size, 'tab')
        packer._original_widget.focus_position.should.be.equal(0)


class test_pane(TestCase):
    def test_non_focused(self):
        content = urwid.Filler(urwid.Text('Hello world!'))
        pane = mainwidget.pane(content, 'my title')

        size = (15, 5)
        rendered = pane.render(size, focus=False).text
        'my title'.should.be.within(rendered[0].decode('utf-8'))
        'Hello world!'.should.be.within(rendered[2].decode('utf-8'))
        '┆'.encode('utf-8').should.be.within(rendered[1])

    def test_focused(self):
        content = urwid.Filler(urwid.Text('Hello world!'))
        pane = mainwidget.pane(content, 'my title')

        size = (15, 5)
        rendered = pane.render(size, focus=True).text
        'my title'.should.be.within(rendered[0].decode('utf-8'))
        'Hello world!'.should.be.within(rendered[2].decode('utf-8'))
        '┃'.encode('utf-8').should.be.within(rendered[1])
