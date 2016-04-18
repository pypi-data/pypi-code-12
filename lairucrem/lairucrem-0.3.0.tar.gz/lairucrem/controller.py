#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""Controller that manage data and connect widgets."""


from __future__ import unicode_literals, absolute_import

from contextlib import contextmanager
import re
import os
import sh
import urwid
import urwid.signals
import urwid.main_loop
from . import widgets, get_extension_path
from .widgets import patchcontent
from .widgets import revisions
from .widgets import mainwidget
from .commands import (get_valid_revision_actions,
                       get_valid_diff_actions, NoRefresh, RefreshPatch)


patch_template = (
    "author: {author}\n"
    "date: {date|isodate}\n"
    "{if(parents, 'parents: {parents}\n')}"
    "{if(children, 'children: {children}\n')}"
    "{if(tags, 'tags: {tags}\n', 'lastest tag: {latesttag} ({latesttagdistance})\n')}"
    "{ifeq(branch, 'default', '', 'branch: {branch}\n')}"
    "{if (bookmarks, 'bookmark: {bookmarks}\n')}"
    "\n{desc}\n\n"
)


#pylint: disable=too-few-public-methods
class _basecontroller(object):
    """Base controller that handle signals"""

    __metaclass__ = urwid.signals.MetaSignals
    def _emit(self, signal, *args):
        """emit the given signal"""
        urwid.emit_signal(self, signal, *args)

    def connect(self, signal, callback):
        """connect the given callback to signal"""
        return urwid.connect_signal(self, signal, callback)

statlinematcher = re.compile(r'^ (.+?) *\| +(\d+ [+-]+$|Bin)')


def interruptable(func):
    """Decorator that inject a coroutine into itself.

    This is useful when the coroutine need to build a callback
    (a.k.a. to be connected to a widget signal) that shall resume
    itself.
    """
    def wrapper(*args, **kwargs):
        """send the coroutine inside itself."""
        coroutine = func(*args, **kwargs)
        coroutine.send(None)
        coroutine.send(coroutine)
    return wrapper


class _patchcontroller(_basecontroller):
    """A small controller dedicated to manage patch content.

    >>> import lairucrem, urwid
    >>> ctrl = _patchcontroller(lairucrem.repository())
    >>> ctrl.refresh(node='')
    """

    signals = ['open_popup', 'monitor_sh', 'run_commands']

    def __init__(self, repo, cache=None):
        super(_patchcontroller, self)
        self._repo = repo
        self._node = ''
        self._cache = cache if cache is not None else {}
        self._tree = patchcontent.patchnode('')
        self._walker = urwid.TreeWalker(self._tree)
        self.widget = patchcontent.treelistbox(self._walker)
        self._connect()

    def refresh(self, node=''):
        """Reset the patch content."""
        self._reset()
        self._node = node
        self._create_process(node)

    def _connect(self):
        """connect signals"""
        urwid.connect_signal(self.widget, 'search', self._search)
        urwid.connect_signal(self.widget, 'commandlist', self._command_list)

    def _reset(self):
        """reset data"""
        self.widget._invalidate()
        self._tree.clear()
        self._walker.set_focus(self._tree)

    def _create_process(self, node):
        """Call mercurial command to update the widget contant"""
        self._reset()
        self._emit('monitor_sh', self._load_patch_description(node), '_load_patch_description')
        self._emit('monitor_sh', self._load_patch_stats(node), '_load_patch_stats')

    def _load_patch_description(self, node):
        """Load the patch description from Hg to the widget"""
        if node:
            yield self._repo.log.bake(rev=node, template=patch_template, hidden=True)
        else:
            yield self._repo.summary.bake(verbose=True) #
        while True:
            data = yield
            if not node:
                #pylint: disable=protected-access
                self._cache.setdefault('summary', {}).update(
                    line.split(':', 1) for line in data.splitlines() if ':' in line
                )
            self._tree.append_description(data)
            self.widget._invalidate()

    def _load_patch_stats(self, node):
        """Load the patch stats from Hg to the widget"""
        if node:
            proc = self._repo.log.bake(rev=node, template=' ', stat=True, hidden=True)
        else:
            # XXX chain with hg status
            proc = self._repo.diff.bake(stat=True, hidden=True)
        yield proc
        while True:
            data = yield
            for line in data.splitlines():
                match = statlinematcher.match(line)
                if not match:
                    continue
                filepath = match.groups()[0].strip()
                getter = lambda node, cset=node, fp=filepath: self._emit(
                    'monitor_sh',
                    self._load_patch_diff(cset, fp, node),
                    ('_load_patch_diff', fp)
                )
                getter.filepath = filepath
                self._tree.append_file(line.strip(), getter)
            self.widget._invalidate()

    def _load_patch_diff(self, cset, filepath, node):
        """Load the patch diff for a specific file from Hg to the widget"""
        yield self._repo.diff.bake(
            filepath, show_function=True, git=True,
            hidden=True, change=cset,
        )
        while True:
            content = yield
            for line in content.splitlines(True):
                node.append_data(line)
            self.widget._invalidate()

    #pylint: disable=unused-argument
    @interruptable
    def _search(self, *args):
        """Display search dialog then process search"""
        myself = yield
        dialog = patchcontent.search(self._tree.search_pattern)
        sigkey = urwid.connect_signal(dialog, 'search', lambda w, q: myself.send(q))
        self._emit('open_popup', dialog)
        query = yield dialog
        urwid.signals.disconnect_signal_by_key(dialog, 'search', sigkey)
        self._tree.expand(recursive=True)
        self._tree.search_pattern = query
        self.widget._invalidate()
        yield myself # prevent raising StopIteration

    #pylint: disable=unused-argument
    def _command_list(self, focus):
        """list related command for user"""
        filepath = focus.get_node().diffgetter.filepath
        try:
            choices, cmds = zip(*get_valid_diff_actions(self._repo, self._node, filepath, self._cache))
        except ValueError: # no actions
            choices, cmds = (), ()
        dialog = widgets.choices(choices)
        urwid.connect_signal(dialog, 'selected',
                             lambda x, c: self._emit('run_commands', cmds[c]))
        self._emit('open_popup', dialog)


#pylint: disable=too-many-instance-attributes
class _revisionscontroller(_basecontroller):
    """
    A small controller dedicated to managed the revisions content.

    >>> import lairucrem
    >>> repo = lairucrem.repository()
    >>> ctrl = _revisionscontroller(repo, template='{desc|firstline}', revset='author(alain)')
    >>> ctrl.refresh()
    """

    signals = ['focus_changed', 'open_popup', 'run_commands', 'redraw']

    def __init__(self, repo, template, revset, cache=None):
        super(_revisionscontroller, self).__init__()
        self._repo = repo
        self._template = r'\0{lairucremid}\0' + template
        self._revset = revset
        self._cache = cache if cache is not None else {}
        self._proc = None
        self._node = None
        self._walker = revisions.walker([])
        self.widget = revisions.listbox(self._walker)
        self._connect()

    def refresh(self):
        """full refresh of the history data."""
        self._reset()
        if self._proc is not None:
            self._proc.terminate()
        proc = self._repo.debuglairucremgraphlog\
               .bake(config='extensions.lairucrem=%s' % get_extension_path())\
               .bake(config="ui.graphnodetemplate={lairucremgraphnode}")
        if self._revset:
            proc = proc.bake(rev=self._revset)
        self._proc = proc(template=self._template, _iter='out')
        self._fill_widget(-1) # non empty is required to ensure urwid take it into account
        self._walker.set_focus(0)
        self._on_focus(0)

    def _reset(self):
        """reset data"""
        self.widget._invalidate()
        del self._walker[:]

    def _connect(self):
        """connect signals"""
        urwid.connect_signal(self.widget, 'commandlist', self._command_list)
        urwid.connect_signal(self.widget, 'filter', self._ask_revset)
        urwid.connect_signal(self._walker, 'need_data', self._fill_widget)
        self._walker.set_focus_changed_callback(self._on_focus)

    def _on_focus(self, pos):
        """called when the focus has changed."""
        self._node = self._walker[pos].node
        self._emit('focus_changed', self._node)

    def _fill_widget(self, pos):
        """Fill the revisions list up to (pos + 1) entries, if available."""
        actually = len(self._walker)
        amount = (pos + 2) - actually
        proc = self._proc
        for dummy in range(amount):
            try:
                self._walker.append_data(next(proc))
            except StopIteration:
                break
        return True

    #pylint: disable=unused-argument
    def _command_list(self, *args):
        """list related command for user"""
        try:
            choices, cmds = zip(*get_valid_revision_actions(self._repo, self._node, self._cache))
        except ValueError: # no actions
            choices, cmds = (), ()
        dialog = widgets.choices(choices)
        urwid.connect_signal(dialog, 'selected',
                             lambda x, c: self._emit('run_commands', cmds[c]))
        self._emit('open_popup', dialog)

    #pylint: disable=unused-argument
    def _ask_revset(self, *args):
        """Ask the revision set expression to apply"""
        dialog = revisions.filterdialog(self._revset)
        urwid.connect_signal(dialog, 'filter', lambda w, r: self._filter(r, w))
        self._emit('open_popup', dialog)
        return dialog

    def _filter(self, revset, dialog=None):
        """Apply the revision set expression to the cset tree"""
        self._revset = revset
        self._emit('redraw') # ensure message are displayed before processing
        try:
            self.refresh()
        except sh.ErrorReturnCode as err:
            if dialog:
                dialog.set_message(err.stderr.strip())
        else:
            if dialog:
                urwid.emit_signal(dialog, 'close')


class controller(object):
    """
    Controller that setup the UI and dispatch data to widgets.
    """

    #mainloop is a good name for me here
    #pylint: disable=redefined-outer-name
    def __init__(self, repo, template, revset, mainloop=None):
        """Return the mainwidget of the application.

        :repo: an sh.Command object that can talk to a mercurial repository
        :template: the mercurial template (as `hg log --template`)

        >>> import lairucrem, urwid
        >>> ml = mainloop(None)
        >>> repo = lairucrem.repository()
        >>> ctrl = controller(repo, template='{rev} {desc}', revset='.::', mainloop=ml)
        >>> ctrl.refresh()
        """
        super(controller, self).__init__()
        self._cache = {}
        self._repo = repo
        self._mainloop = None
        self._monitored_sh = {}
        self._patch_ctrl = _patchcontroller(self._repo, self._cache)
        self._revisions_ctrl = _revisionscontroller(self._repo, template, revset, self._cache)
        self._content = mainwidget.mainwidget(mainwidget.packer([
            mainwidget.pane(self._revisions_ctrl.widget, 'TREE'),
            mainwidget.pane(self._patch_ctrl.widget, 'PATCH'),
        ]))
        self.widget = mainwidget.popuplauncher(self._content)
        self._connect()
        if mainloop:
            self._mainloop = mainloop
            mainloop.widget = self.widget

    def refresh(self):
        """refresh the whole data"""
        self._cache.clear()
        self._revisions_ctrl.refresh()

    def _refresh_patch(self):
        self._patch_ctrl.refresh(self._patch_ctrl._node)

    def _connect(self):
        """connect signals"""
        self._revisions_ctrl.connect('focus_changed', self._on_cset_selected)
        self._revisions_ctrl.connect('open_popup', self._open_popup)
        self._patch_ctrl.connect('open_popup', self._open_popup)
        self._revisions_ctrl.connect('run_commands', self._run_interactive_command)
        self._patch_ctrl.connect('run_commands', self._run_interactive_command)
        self._revisions_ctrl.connect('redraw', self._redraw)
        self._patch_ctrl.connect('monitor_sh', self._monitor_sh)
        urwid.connect_signal(self._content, 'open_popup', self._open_popup)

    def _on_cset_selected(self, node):
        """set the selected cset from the given tree entry position."""
        self._patch_ctrl.refresh(node)


    @interruptable
    def _run_interactive_command(self, cmds):
        """Interrupt the interface the run the given command `cmd`.

        The arguments are directly passed to subprocess.Popen
        """
        continuator = yield
        refresh = True
        with self._mainloop.interrupt():
            try:
                while True:
                    try:
                        value = cmds.send(cmds)
                        if isinstance(value, urwid.Widget):
                            urwid.connect_signal(value, 'close', lambda *a: next(continuator))
                            with self._mainloop.futher():
                                self._open_popup(value)
                                yield
                    except StopIteration:
                        break
                    except OSError as err:
                        with self._mainloop.futher():
                            self._open_popup(
                                widgets.simpledialog(urwid.Text(('error', str(err))), 'ERROR'))
                    except NoRefresh:
                        refresh = False
                        break
                    except RefreshPatch:
                        refresh = False
                        self._refresh_patch()
            finally:
                if refresh:
                    self.refresh()
        yield

    def _open_popup(self, dialog):
        """put dialog in a popup"""
        self.widget.open_pop_up(dialog)

    #pylint: disable=unused-argument
    def _redraw(self, *args):
        """redraw the screen"""
        #I've no other choices pylint
        #pylint: disable=protected-access
        if self._mainloop.screen._started:
            self._mainloop.force_redraw_screen()

    def _monitor_sh(self, coroutine, key):
        """Retrieve a baked process from the coroutine that is started and
        monitored by the mainloop. Any process output it send back to the
        coroutine.

        Kill any running process monitored with the same 'key'.
        """
        if key in self._monitored_sh:
            outstream, proc = self._monitored_sh.pop(key)
            proc.terminate()
            #pylint: disable=bare-except
            try:
                proc.wait() # the pipe should be closed once the process is really
            except:
                pass        # terminated to prevant it to write on broken file desc
            finally:
                self._mainloop.remove_watch_pipe(outstream.fileno())
        outstream = os.fdopen(self._mainloop.watch_pipe(coroutine.send), 'w')
        baked = coroutine.send(None)
        proc = baked(_out=outstream, _iter=True) # XXX close and unregister pipe,
        coroutine.send(proc)
        self._monitored_sh[key] = outstream, proc


class mainloop(urwid.MainLoop):
    """Patched mainloop with new useful methods"""
    def __init__(self, *args, **kwargs):
        super(mainloop, self).__init__(*args, **kwargs)
        self._uniq_alarms = {}
        self._force_redraw_pipe = self.watch_pipe(lambda *a: self.draw_screen)

    def force_redraw_screen(self):
        """ensure redrawing the screen even from other thread"""
        os.write(self._force_redraw_pipe, '\1')

    def watch_pipe(self, callback):
        """patched watch_pipe providing a gentle cb"""
        # patched version
        import fcntl
        pipe_rd, pipe_wr = os.pipe()
        fcntl.fcntl(pipe_rd, fcntl.F_SETFL, os.O_NONBLOCK)
        watch_handle = None

        #pylint: disable=invalid-name
        #pylint: disable=missing-docstring
        def cb():
            try:
                data = os.read(pipe_rd, urwid.main_loop.PIPE_BUFFER_READ_SIZE)
            except OSError:
                # conflicts may appears because of concurrent threads.
                # We just ignore them instead of raising an error (which
                # close the application). This appears when the user
                # quickly scroll the tree, so we can ignore gently
                # ignore it
                return
            rval = callback(data)
            if rval is False:
                self.event_loop.remove_watch_file(watch_handle)
                os.close(pipe_rd)

        watch_handle = self.event_loop.watch_file(pipe_rd, cb)
        self._watch_pipes[pipe_wr] = (watch_handle, pipe_rd)
        return pipe_wr


    @contextmanager
    def interrupt(self):
        """Context manager to execute things outside the mainloop"""
        self.stop() #pylint: disable=no-member
        yield
        self.start() #pylint: disable=no-member

    @contextmanager
    def futher(self):
        """Context manager to execute things inside the mainloop"""
        self.start() #pylint: disable=no-member
        yield
        self.stop() #pylint: disable=no-member
