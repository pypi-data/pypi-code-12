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
import urwid
import re

from lairucrem.widgets import patchcontent

DIFFS = {
    'lairucrem/widgets/foo.py': '''
diff --git a/lairucrem/widgets/foo.py b/lairucrem/widgets/foo.py
hello
--- a/lairucrem/widgets/patchcontent.py
+++ b/lairucrem/widgets/patchcontent.py
@@ -12,6 +12,9 @@ import urwid

+TEST = False
+
 class _tree_node(urwid.ParentNode):

@@ -30,7 +33,7 @@ class _tree_node(urwid.ParentNode):
     def load_widget(self):
-        """return the node widget"""
+        """Return a non-expanded widget node"""
         return _tree_node_widget(self)

    ''',
    'lairucrem/widgets/bar.py': '''
diff --git a/lairucrem/widgets/bar.py b/lairucrem/widgets/bar.py
hello
--- a/lairucrem/widgets/patchcontent.py
+++ b/lairucrem/widgets/patchcontent.py
@@ -12,6 +12,9 @@ import urwid

+TEST = False
+
 class _tree_node(urwid.ParentNode):
'''
}

def _get_diff(filename, n):
    for line in DIFFS[filename].splitlines(False):
        n.append_data(line)

STAT = (
    (' lairucrem/widgets/foo.py |  42 +++--\n', 'lairucrem/widgets/foo.py'),
    (' lairucrem/widgets/bar.py |  24 +++--\n', 'lairucrem/widgets/bar.py'),
    )

DESC = (
    'hello: world\n',
    '\n',
    'toto\n',
    '\n',
    )

class test_node(TestCase):
    def setUp(self):
        self.root = patchcontent._tree_node('root')
        self.subnodes = []
        self.subsubnodes = []
        for i in xrange(5):
            subnode = patchcontent._tree_node('subnode%i' %i)
            self.subnodes.append(subnode)
            self.root._children.append(subnode)
            for j in xrange(3):
                subsubnode = patchcontent._tree_node('subsubnode%i' %i)
                self.subsubnodes.append(subsubnode)
                subnode._children.append(subsubnode)

    def test_clear(self):
        self.root.clear()
        (1).should.equal(len(self.root._children))
        self.root._value.should.be.falsy
        self.root._children[0]._value.should.be.falsy

        self.root._children[0]._value = 'toto'
        self.root._children[0].clear()
        self.root._children[0]._value.should.be.falsy

    def test_navigate(self):
        self.root.has_children().should.be.truthy
        isinstance(self.root._children[0], patchcontent._leaf).should.be.truthy

        self.root.get_first_child().should.be(self.root._children[0])
        self.root.get_last_child().should.be(self.subnodes[-1])

        (self.subnodes[0]).should.be(self.root.next_child(0))
        self.root.next_child(5).should.be.falsy

        (self.subnodes[0]).should.be(self.root.prev_child(2))
        self.root.prev_child(0).should.be.falsy

        (0).should.equal(self.root.get_child_index(0))
        list(range(len(self.subnodes) + 1)).should.equal(self.root.load_child_keys())

        self.subnodes[1].should.be(self.root.load_child_node(2))


class test_node_widget(TestCase):
    def setUp(self):
        self.root = patchcontent._tree_node('root')
        self.subnodes = []
        self.subsubnodes = []
        for i in xrange(5):
            subnode = patchcontent._tree_node('subnode%i' %i)
            self.subnodes.append(subnode)
            self.root._children.append(subnode)
            for j in xrange(3):
                subsubnode = patchcontent._tree_node('subsubnode%i' %i)
                self.subsubnodes.append(subsubnode)
                subnode._children.append(subsubnode)

    def test_keypress_leaf(self):
        size = (10, 10)
        widget = self.root._children[0].get_widget()
        'left'.should.equal(widget.keypress(size, 'left'))

    def test_keypress_node(self):
        size = (10, 10)
        widget = self.root.get_widget()
        self.root.unexpand(recursive=True)
        widget.keypress(size, 'right').should.be.falsy
        widget.expanded.should.be.truthy
        b'down'.should.equal(widget.keypress(size, 'right'))

        widget.keypress(size, 'left').should.be.falsy
        widget.expanded.should.be.falsy

        widget.keypress(size, 'enter').should.be.truthy


def test_patch_node():
    node = patchcontent.patchnode(' ')
    for line in DESC:
        node.append_description(line)
    for line, filepath in STAT:
        node.append_file(line, None)

    # 3 children: description + 2 file diffs
    (3).must.be(len(node._children))
    node._children[0]._value.should.equal('hello: world\n\ntoto\n\n')
    dn = node._children[1]
    ' lairucrem/widgets/foo.py |  42 +++--'.should.be.within(dn._value)


def test_diff_and_chunk_nodes():
    node = patchcontent._diffnode(
        ' lairucrem/widgets/foo.py |  42 +++--',
        diffgetter=lambda n: _get_diff('lairucrem/widgets/foo.py', n),
        parent=None, key=None
    )
    ' lairucrem/widgets/foo.py |  42 +++--'.should.equal(node._value)

    node._fill_data()

    (3).should.equal(len(node._children))


    'diff --git'.should_not.be.within(node._children[0]._value) # skip diff --git line
    'hello'.should.be.within(node._children[0]._value)

    chunknode = node._children[1]
    '@@ -12,6 +12,9'.should.be.within(chunknode._value)
    (1).should.equal(len(chunknode._children))
    '+TEST = False'.should.be.within(chunknode._children[0]._value)

    chunknode = node._children[2]
    '@@ -30,7 +33,7'.should.be.within(chunknode._value)
    (1).should.equal(len(chunknode._children))
    '-        """return the node widget"""'.should.be.within(chunknode._children[0]._value)


def test_expand_unexpand():
    node = patchcontent.patchnode(' ')
    for line in DESC:
        node.append_description(line)
    for line, filepath in STAT:
        node.append_file(line, lambda n, fp=filepath: _get_diff(fp, n))
    widget = patchcontent.treelistbox(urwid.TreeWalker(node))

    # folded by default
    assert not any([isinstance(n, patchcontent._chunknode) for n in widget])

    # expand all, we can see that expanding _diffnode automatically load chunks data
    node.expand(recursive=True)
    assert any([isinstance(n, patchcontent._chunknode) for n in widget])

    chunk = next(n for n in widget if isinstance(n, patchcontent._chunknode))

    # unexpand all
    node.unexpand(recursive=True)
    assert not any([isinstance(n, patchcontent._chunknode) for n in widget])


def test_search_diaglog():
    dialog = patchcontent.search(re.compile('hello'))
    unicode(dialog.edit.get_edit_text()).should.equal('hello')

    events = []
    urwid.connect_signal(dialog, 'search', lambda w, p: events.append(p))
    urwid.connect_signal(dialog, 'close', lambda w: events.append('closed'))

    # let simulate user taping pattern
    del events[:]
    size = (10, 10)
    for letter in ' world':
        dialog.keypress(size, letter)
    dialog.keypress(size, 'enter')
    len(events).should.equal(2)
    events[0].pattern.should.equal(b'hello world')
    events[1].should.equal('closed')

    # now user cancel
    del events[:]
    size = (10, 10)
    for letter in b'hello world':
        dialog.keypress(size, letter)
    dialog.keypress(size, 'esc')
    len(events).should.equal(1)
    events[0].should.equal('closed')

    # user provides a wrong regexp
    # now user cancel
    del events[:]
    size = (10, 10)
    for letter in '(hello world':
        dialog.keypress(size, letter)
    dialog.keypress(size, 'enter')
    len(events).should.equal(0)
    'unbalanced parenthesis'.should.be.within(dialog.message.get_text()[0])

def test_treelistbox_keypress():
    node = patchcontent.patchnode(' ')
    for line in DESC:
        node.append_description(line)
    for line, filepath in STAT:
        node.append_file(line, lambda n, fp=filepath: _get_diff(fp, n))
    widget = patchcontent.treelistbox(urwid.TreeWalker(node))
    size = (100, 100)

    #root focused, should release key
    widget.keypress(size, 'left').should.be.truthy

    # go down
    widget.keypress(size, 'right').should.be.falsy # diff
    widget.keypress(size, 'right').should.be.falsy # chunk
    widget.keypress(size, 'right').should.be.falsy # down
    widget.keypress(size, 'right').should.be.falsy # down

    # go up
    widget.keypress(size, 'left').should.be.falsy # chunk
    widget.keypress(size, 'left').should.be.falsy # diff


def test_searching_pattern():
    node = patchcontent.patchnode(' ')
    for line in DESC:
        node.append_description(line)
    for line, filepath in STAT:
        node.append_file(line, lambda n, fp=filepath: _get_diff(fp, n))
    widget = patchcontent.treelistbox(urwid.TreeWalker(node))

    size = (10, 10)

    # check ask for search dialog
    events = []
    urwid.connect_signal(widget, 'search', lambda w: events.append('search'))
    widget.keypress(size, '/')
    events.should.be.truthy
