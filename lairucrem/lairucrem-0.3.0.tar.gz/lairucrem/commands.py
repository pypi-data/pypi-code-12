#! /usr/bin/env python
# coding: utf-8
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""Commands that can be processed depending on a given changeset."""

from tempfile import mkstemp
import os
import shlex

import urwid

from subprocess import call

from . import runsh
from .widgets import multiplechoices, choices

revision_cmd_registry = []
diff_cmd_registry = []


class NoRefresh(Exception):
    """Exception that should be raised by the command that does not
    requires a refresh of the history tree data
    """

class RefreshPatch(Exception):
    """Exception that should be raised by the command that want to
    refresh patch only.
    """
# registry can be changed for test purpose
# pylint: disable=dangerous-default-value
def get_valid_revision_actions(repo, cset, cache=None, registry=revision_cmd_registry):
    """Return the list of actions that can be applied to the given changeset"""
    cache = {'global': cache if cache is not None else {}}
    iter_actions = ((name, func(repo, cset, cache)) for func, name in registry)
    return [(choice, _cmd) for choice, _cmd in iter_actions if next(_cmd)]


def get_valid_diff_actions(repo, cset, filepath, cache=None, registry=diff_cmd_registry):
    """Return the list of actions that can be applied to the given file diff"""
    cache = {'global': cache if cache is not None else {}}
    iter_actions = ((name, func(repo, cset, filepath, cache)) for func, name in registry)
    return [(choice, _cmd) for choice, _cmd in iter_actions if next(_cmd)]


# registry can be changed for test purpose
# pylint: disable=dangerous-default-value
def cmd(name=None, replace=None, _registry=revision_cmd_registry):
    """Decorator that registers a command function.

    :name: name displayed in the choice menu
           or the decorated function name if not given.

    :replace: (func, name), if given, is replaced by the current one.
    """
    def wrapper(func=None):
        """wrapper that register the command"""
        _name = name or func.__name__
        if replace and replace in _registry:
            _registry[_registry.index(replace)] = (func, _name)
        else:
            _registry.append((func, _name))
        return func
    return wrapper


# commands
# ########

@cmd(name='Commit: commit all outstanding changes')
def commit(repo, cset, _cache):
    """Commit all outstanding changes

    Commit changes to the given files into the repository using the interactive mode.
    Add '[experimental] crecord=true' in the HGRC for a curses base interface.
    """
    yield not cset and not is_clean(repo, cset, _cache)
    runsh(repo.commit.bake(
        interactive=True, edit=True, config="experimental.crecord=true"))


@cmd(name='Amend: amend the parent of the working directory')
def amend(repo, cset, _cache):
    """Amend the parent of the working directory

    with new commit that contains the changes in the parent in
    addition to those currently outstanding.

    Add '[experimental] crecord=true' in the HGRC for a curses base
    interface.
    """
    yield not cset and not is_clean(repo, cset, _cache)
    runsh(repo.commit.bake(
        interactive=True, amend=True, edit=True, config="experimental.crecord=true"))


@cmd(name='addremove: add all new files, delete all missing files')
def addremove(repo, cset, _cache):
    """add all new files, delete all missing files.
    """
    summary = get_summary(repo, cset, _cache)['commit']
    continuator = (yield not cset and ('unknown' in summary or 'deleted' in summary))
    entries = [entry.strip() for entry in repo.status(deleted=True, unknown=True)]
    dialog = multiplechoices(entries, (
        ('apply', 'meta enter', 'Add new files and delete missing files'),
        ('fix', None, 'Purge new files and revert missing files'),
    ))
    urwid.connect_signal(dialog, 'selected', lambda w, c: continuator.send(c))
    urwid.connect_signal(dialog, 'close', lambda *a: continuator.close())
    data = yield dialog
    if data:
        action, selected = data
        if action == 'apply':
            files = [entries[idx][2:].encode('utf-8') for idx in selected]
            runsh(repo.addremove.bake(files))
        elif action == 'fix':
            selected = [entries[idx].encode('utf-8') for idx in selected]
            unknowns = [entry[2:] for entry in selected if entry.startswith('?')]
            deleteds = [entry[2:] for entry in selected if entry.startswith('!')]
            if unknowns:
                runsh(repo.bake(config='extensions.purge=').purge.bake(*unknowns))
            if deleteds:
                runsh(repo.revert.bake(*deleteds))
    yield


@cmd(name='Shelve: save and set aside changes from the working directory')
def shelve(repo, cset, _cache):
    """Save and set aside changes from the working directory.

    Shelvinf takes files from the durty working directory, saves the
    modifications to a bundle and reverts files so that their state in
    the working directory becomes clean.
    """
    yield not cset and not is_clean(repo, cset, _cache)
    runsh(repo.shelve
          .bake(config="experimental.crecord=true")
          .bake(config='extensions.hgext.shelve=', interactive=True, edit=True))


#pylint: disable=unused-argument
@cmd(name='Unshelve: restore a shelved change to the working directory')
def unshelve(repo, cset, _cache):
    """Check if they are shelved, if so list them"""
    shelves = [line.strip()
               for line in list(repo.shelve(list=True, config='extensions.hgext.shelve='))]
    continuator = yield not cset and bool(shelves)
    dialog = choices(shelves)
    urwid.connect_signal(dialog, 'selected', lambda w, c: continuator.send(c))
    urwid.connect_signal(dialog, 'close', lambda *a: continuator.close())
    selected = yield dialog
    if selected is not None:
        name = shelves[selected].split()[0]
        runsh(repo.unshelve.bake(name, config='extensions.hgext.shelve='))
    yield


@cmd(name='Update: update working directory (or switch revisions)')
def update(repo, cset, _cache):
    """Update working directory (or switch revisions)

    Update the repository's working directory to the specified changeset.
    """
    yield cset and not is_cwd(repo, cset, _cache)
    runsh(repo.update.bake(rev=cset))


@cmd(name='Histedit: edit the chunck of history between cwd and selected')
def histedit(repo, cset, _cache):
    """perform `histedit' if the repository is clean"""
    # XXX check if selected is before cwd but it may take a while :/
    yield cset and is_clean(repo, cset, _cache) and not is_cwd(repo, cset, _cache)
    runsh(repo.histedit.bake(config='extensions.hgext.histedit=', rev=cset))


@cmd(name='Rebase: move changeset (and descendants) onto of the working directory')
def rebase(repo, cset, _cache):
    """Move changeset (and descendants) onto of the working directory"""
    yield cset and is_rebasable(repo, cset, _cache)
    runsh(repo.rebase.bake(config='extensions.hgext.rebase=', source=cset, dest='.'))
    runsh(repo.update.bake(rev='tip'))


@cmd(name='rebase one: move changeset onto the working directory')
def rebase_one(repo, cset, _cache):
    """Move changeset onto the working directory"""
    yield cset and is_rebasable(repo, cset, _cache)
    runsh(repo.rebase.bake(config='extensions.hgext.rebase=', rev=cset, dest='.'))
    runsh(repo.update.bake(rev='tip'))


@cmd(name='Graft: copy changes from other branches onto the working direstory')
def graft(repo, cset, _cache):
    """Copy changes from other branches onto the working direstory"""
    yield cset and is_rebasable(repo, cset, _cache)
    runsh(repo.graft.bake(rev=cset))


@cmd(name="Draft: mark the changeset as draft")
def draft(repo, cset, _cache):
    """Set the changeset as draft"""
    yield cset and get_phase(repo, cset, _cache) == 'secret'
    runsh(repo.phase.bake(draft=True, rev=cset))


@cmd(name="public: mark the changeset as public")
def public(repo, cset, _cache):
    """Set the changeset as draft"""
    yield cset and get_phase(repo, cset, _cache) != 'public'
    runsh(repo.phase.bake(public=True, rev=cset))


@cmd(name="Push: push changes to the default destination")
def push(repo, cset, _cache):
    """push changes to the default destination"""
    continuator = yield cset and get_phase(repo, cset, _cache) != 'secret'
    paths = [l[6:].strip().split('=') for l in repo.showconfig('paths')]
    if len(paths) > 1:
        maxlen = max(len(path[0]) for path in paths)
        dialog = choices(['%s: %s' % (path[0].rjust(maxlen), path[1]) for path in paths])
        urwid.connect_signal(dialog, 'selected', lambda w, c: continuator.send(c))
        urwid.connect_signal(dialog, 'close', lambda *a: continuator.close())
        selected = yield dialog
    else:
        selected = 0
    dest = paths[selected][0]
    runsh(repo.push.bake(dest, rev=cset, new_branch=True))
    yield


@cmd(name='Revert: restore all files to the selected chechout state')
def revert(repo, cset, _cache):
    """perform 'revert --all' depending on cset if the repository is not
    clean or selected is not cwd"""
    yield cset or not is_clean(repo, cset, _cache)
    if cset:
        runsh(repo.revert.bake(rev=cset, all=True))
    else:
        runsh(repo.revert.bake(all=True))
    raise NoRefresh()


@cmd(name='Edit description: amend changeset description and rebase unstables')
def edit_description(repo, cset, _cache):
    """Perform multiple tasks (update, amend, rebase) to edit the commit
    description."""
    yield cset and is_clean(repo, cset, _cache) and get_phase(repo, cset, _cache) != 'public'
    revset = 'children(%(n)s)' % {'n': cset}
    torebase = unicode(repo.log(template='{node},', rev=revset)).strip()
    runsh(repo.update.bake(rev=cset))
    runsh(repo.commit.bake(edit=True, amend=True))
    if not torebase:
        return
    newcset = unicode(repo.log(limit=1, template='{node}')).strip()
    for node in torebase.split(','):
        node = node.strip()
        if node:
            runsh(repo.rebase.bake(
                config='extensions.hgext.rebase=', source=node, dest=newcset))


############ DIFF #######################

@cmd('Revert: restore the file to the selected chechout state', _registry=diff_cmd_registry)
def revert_file(repo, cset, filepath, _cache):
    """perform 'revert --all' depending on cset if the repository is not
    clean or selected is not cwd"""
    yield cset or not is_clean(repo, cset, _cache)
    if cset:
        runsh(repo.revert.bake(filepath, rev=cset))
        raise NoRefresh()
    else:
        runsh(repo.revert.bake(filepath))
        raise RefreshPatch()


@cmd('open: open the file at the selected revision in $EDITOR', _registry=diff_cmd_registry)
def open_file(repo, cset, filepath, _cache):
    """perform 'revert --all' depending on cset if the repository is not
    clean or selected is not cwd"""
    yield True
    editor = shlex.split(os.environ['EDITOR']) or ['vim']
    if cset:
        fd, name = mkstemp(suffix='_' + os.path.basename(filepath))
        try:
            try:
                runsh(repo.cat.bake(filepath, rev=cset), stdout=fd)
            finally:
                os.close(fd)
            call(editor + [name])
        finally:
            os.remove(name)
        raise NoRefresh()
    else:
        call(editor + [filepath])
        raise RefreshPatch()



@cmd('remove: remove the specified files on the next commit', _registry=diff_cmd_registry)
def remove_file(repo, cset, filepath, _cache):
    yield not cset or is_cwd(repo, cset, _cache)
    if not cset:
        runsh(repo.remove.bake(filepath, force=True))
    else:
        runsh(repo.remove.bake(filepath))
    raise RefreshPatch()


# tests
# #####

def is_rebasable(repo, cset, _cache):
    """Return True if the given cset can be rebased"""
    if is_cwd(repo, cset, _cache) or get_phase(repo, cset, _cache) == 'public':
        _cache['rebasable'] = False
    elif not _cache.get('rebasable'):
        revset = 'ancestor(%(c)s,.) and not %(c)s' % {'c': cset}
        _cache['rebasable'] = bool(unicode(repo.log(rev=revset, template="{node}")))
    return _cache['rebasable']

def get_phase(repo, cset, _cache):
    """Return the phase name of the cset"""
    if not _cache.get('phase'):
        _cache['phase'] = unicode(repo.log(rev=cset, template="{phase}"))
    return _cache['phase']

def is_cwd(repo, cset, _cache):
    """Return True if the given cset is the parent of the working directory"""
    parent = unicode(get_summary(repo, cset, _cache)['parent'])
    return parent.split(':', 1)[1][:12] == cset.split(':', 1)[1][:12]

def is_clean(repo, cset, _cache):
    """Return True if the working directory is not durty"""
    return 'clean' in get_summary(repo, cset, _cache)['commit']

#pylint: disable=unused-argument
#pylint: disable=protected-access
def get_summary(repo, cset, _cache):
    """Return `hg summary -v`"""
    globalcache = _cache.get('global', {})
    if not globalcache.get('summary'):
        globalcache.setdefault('summary', {}).update(
            line.split(':', 1) for line in repo.summary(verbose=True) if ':' in line)
    return globalcache['summary']
