# -*- encoding: utf-8 -*-
#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""UI widgets to display patch content."""

import re
import urwid
from . import lightbutton, text

__all__ = ['patchnode', 'treelistbox']


class _tree_node(urwid.ParentNode):
    """Tree Node managed using a list. This class is mostly a
    smplification of urwid.ParentNode.

    The tree node always has a leaf node as first child that contains
    data of the node itself.
    """
    def __init__(self, *args, **kwargs):
        super(_tree_node, self).__init__(*args, **kwargs)
        self._children = [_leaf(value='', parent=self, key=0)]

    def clear(self):
        """reset node content (remove all subnodes an clean the first leaf)"""
        self._value = ''
        self._children = [_leaf(value='', parent=self, key=0)]
        self._widget = None

    def load_widget(self):
        """return the node widget"""
        return _tree_node_widget(self)

    def get_child_index(self, key):
        """noop"""
        return key

    def next_child(self, key):
        """return the child after to the focused one"""
        if key is None or key >= len(self._children) -1:
            return None
        return self.get_child_node(key + 1)

    def prev_child(self, key):
        """return the child before to the focused one"""
        if key is None or key <= 0:
            return None
        return self.get_child_node(key - 1)

    def get_first_child(self):
        """return the first child (a.k.a. the first leaf used for node
        date)"""
        return self._children[0]

    def get_last_child(self):
        """return the last child"""
        return self._children[-1]

    def has_children(self):
        """always return True has their is at least the leaf for node data."""
        return True

    def load_child_keys(self):
        """return the index of each children in order: range(len(children))"""
        return range(len(self._children))

    def load_child_node(self, key):
        """return the child at the given index"""
        return self._children[key]

    def expand(self, recursive=True):
        """expand the node"""
        if self._widget and not self._widget.is_leaf:
            self._widget.expanded = True
            self._widget.update_expanded_icon()
        if recursive and self._children:
            for child in self._children:
                child.expand(recursive=recursive)

    def unexpand(self, recursive=True):
        """collaps the node"""
        if self._widget and not self._widget.is_leaf:
            self._widget.expanded = False
            self._widget.update_expanded_icon()
            self._widget._invalidate()
        if recursive and self._children:
            for child in self._children:
                child.unexpand(recursive=recursive)


class patchnode(_tree_node):
    """A tree node that handles the whole patch content."""
    def __init__(self, *args, **kwargs):
        self.search_pattern = None
        super(patchnode, self).__init__(*args, **kwargs)

    def append_description(self, line):
        """add description lines"""
        self._children[0].append_data(line)

    def append_file(self, line, diffgetter):
        """Add a new line of the patch. It will be broadcasted to children if
        needed"""
        node = _diffnode(value=line, parent=self, key=len(self._children), diffgetter=diffgetter)
        self._children.append(node)

    def load_widget(self):
        """return the node widget"""
        return _tree_root_widget(self)


class _diffnode(_tree_node):
    """A tree node that handles each file part a.k.a. 'diff --git'"""

    def __init__(self, *args, **kwargs):
        self.diffgetter = kwargs.pop('diffgetter')
        self._data_loaded = False
        super(_diffnode, self).__init__(*args, **kwargs)

    def append_data(self, line):
        """Add a new line of the file patch. It will be broadcasted to
        children if needed"""
        if line.startswith('diff --git '):
            return
        if line.startswith('@@ '):
            self._children.append(_chunknode(value=line, parent=self, key=len(self._children)))
        else:
            self._children[-1].append_data(line)

    def load_widget(self):
        """Return a non-expanded widget node"""
        widget = _tree_diff_widget(self)
        widget.expanded = False
        widget.update_expanded_icon()
        urwid.connect_signal(widget, 'expand', self._fill_data)
        return widget

    #pylint: disable=unused-argument
    def _fill_data(self, *args, **kwargs):
        """request for diff content"""
        if not self._data_loaded and self.diffgetter:
            self.diffgetter(self)
            self._data_loaded = True


class _chunknode(_tree_node):
    """A tree node that handles a patch chunk, a.k.a. '@@ '"""
    def append_data(self, line):
        """Add a new line of the chunck."""
        self._children[-1].append_data(line)


class _leaf(urwid.TreeNode):
    """Tree leaf used for data of the node itself."""
    def clear(self):
        """clear text"""
        self._value = ''

    #pylint: disable=unused-argument
    def expand(self, *args, **kwargs):
        """expand the node"""
        pass

    #pylint: disable=unused-argument
    def unexpand(self, *args, **kwargs):
        """collaps the node"""
        pass

    def append_data(self, line):
        """Add new text"""
        self._value += line

    def load_widget(self):
        """return node widget"""
        return _tree_widget(self)


class _tree_widget(urwid.TreeWidget):
    """Widget for tree/leaf nodes. Node content is highlighted."""
    indent_cols = 1
    unexpanded_icon = urwid.SelectableIcon('^', 0)
    expanded_icon = urwid.SelectableIcon('>', 0)

    def _get_default_style(self):
        """return the palette name of the default style"""
        return 'default' if self.is_leaf else 'important'

    def load_inner_widget(self):
        """Return the 'graphical' widget"""
        style = self._get_default_style()
        getter = lambda self=self: self.get_node().get_root().search_pattern
        inner = text((style, self.get_node().get_value()),
                     default_style=style,
                     search_pattern_getter=getter)
        return inner

    def get_indented_widget(self):
        """Return the 'graphical' widget indented accordlingly to its tree
        depth"""
        widget = self.get_inner_widget()
        if not self.is_leaf:
            widget = urwid.Columns([
                ('fixed', 1, [self.unexpanded_icon, self.expanded_icon][self.expanded]),
                widget
            ], dividechars=0)
        indent_cols = self.indent_cols * max((self.get_node().get_depth() -1), 0)
        return urwid.Padding(widget, width=('relative', 100), left=indent_cols)

    def _invalidate(self):
        """invalidte cache"""
        self._innerwidget = None
        self._wrapped_widget = self.get_indented_widget()
        super(_tree_widget, self)._invalidate()


class _tree_node_widget(_tree_widget):
    """Same as _tree_widget but provides shortkeys a la crecord."""
    def keypress(self, size, key):
        """Handle expand & collapse requests (non-leaf nodes)"""
        if key == "+" or (self._command_map[key] == 'cursor right' and not self.expanded):
            self.expanded = True
            self.update_expanded_icon()
        elif self._command_map[key] == 'cursor right':
            return super(_tree_node_widget, self).keypress(size, 'down')
        elif key == "-" or (self._command_map[key] == 'cursor left' and self.expanded):
            self.expanded = False
            self.update_expanded_icon()
        elif self._w.selectable():
            return super(_tree_node_widget, self).keypress(size, key)
        else:
            return key

class _tree_diff_widget(_tree_node_widget):
    """Widet for _diff_node"""
    signals = ['expand']

    def update_expanded_icon(self):
        """change the expand icon"""
        if self.expanded:
            self._emit('expand')
        return super(_tree_diff_widget, self).update_expanded_icon()

    def keypress(self, size, key):
        key = super(_tree_diff_widget, self).keypress(size, key)
        if key == 'enter':
            return 'commandlist'
        return key


class _tree_root_widget(_tree_node_widget):
    """widget for patchnode"""
    def selectable(self):
        return True

    def get_indented_widget(self):
        """return the indented inner widget"""
        return urwid.Text('')

    def update_expanded_icon(self):
        """change the expand icon"""
        pass

    def keypress(self, size, key):
        """Handle expand & collapse requests (non-leaf nodes)"""
        if self._command_map[key] == 'cursor right':
            key = 'down'
        if self._w.selectable():
            return super(_tree_root_widget, self).keypress(size, key)
        else:
            return key


class treelistbox(urwid.TreeListBox):
    """List box for the patch node tree"""
    signals = ['search', 'commandlist']

    def keypress(self, size, key):
        """process keypress"""
        if self._command_map[key] == 'cursor left':
            pos = self.body.get_focus()[1]
            #pylint sucks
            #pylint: disable=no-member
            parentpos = pos.get_parent()
            if parentpos is None:
                return key
        elif key == '/':
            self._emit('search')
        key = super(treelistbox, self).keypress(size, key)
        if key == 'commandlist':
            urwid.emit_signal(self, 'commandlist', self.focus)
        else:
            return key

    def _invalidate(self):
        """invalidate cache"""
        for node in self:
            node.get_widget()._invalidate()
        super(treelistbox, self)._invalidate()


class search(urwid.WidgetWrap):
    """ddialog for search pattern inside a patch content"""

    signals = ['close', 'search']

    def __init__(self, pattern):
        self.setup_ui(pattern)
        urwid.connect_signal(self.closer, 'click', lambda button: self._cancel())
        urwid.connect_signal(self.applier, 'click', lambda button: self._search())
        super(search, self).__init__(urwid.AttrWrap(self.fill, 'highlight'))

    @staticmethod
    def get_rows():
        """prefered height"""
        return 10

    def setup_ui(self, pattern):
        """setup widgets"""
        self.closer = lightbutton("[esc] Cancel")
        self.applier = lightbutton("[enter] Search")
        self.edit = urwid.Edit("", unicode(pattern.pattern) if pattern else '')
        self.message = urwid.Text('')
        pile = urwid.Pile([
            urwid.Divider(),
            urwid.Text('Regular expression pattern:'),
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
                                  title='Highlight pattern in patch')

    #pylint: disable=unused-argument
    def _search(self, *args):
        """send signal to apply the revset."""

        pattern = self.edit.edit_text
        if pattern:
            try:
                pattern = re.compile(pattern)
            except re.error as err:
                self.message.set_text(unicode(err))
                return
        self._emit('search', pattern)
        self._emit('close')

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
        #pylint sucks
        #pylint: disable=not-callable
        return super(search, self).keypress(size, key)
