#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""Mercurial extension for lairucrem.

This extension provides utilities that are executed in the repository
side.
"""

import itertools
from mercurial import cmdutil, graphmod, i18n, templatekw
from mercurial.node import nullid


def showid(repo, ctx, templ, **args):
    """:lairucremid: String. The cset identifier as `rev:node`"""
    if ctx.rev() is None:
        return ''
    return '%s:%s' % (templatekw.showrev(repo, ctx, templ, **args),
                      templatekw.shownode(repo, ctx, templ, **args))


#bha, 'return out' seems uglier than this
#pylint: disable=too-many-return-statements
#pylint: disable=too-many-branches
#pylint: disable=unused-argument
def showgraphnode(repo, ctx, **args):
    """:graphnode: String. The character representing the changeset node in
    an ASCII revision graph"""
    wpnodes = repo.dirstate.parents()
    if wpnodes[1] == nullid:
        wpnodes = wpnodes[:1]
    if ctx.node() in wpnodes:
        return '@'
    elif ctx.obsolete():
        return 'x'
    elif ctx.closesbranch():
        return '_'
    elif ctx.troubled():
        return '!'
    elif ctx.phase() == 0:
        return '0'
    elif ctx.phase() == 1:
        return 'o'
    elif ctx.phase() == 2:
        return '.'
    else:
        return 'o'


templatekw.keywords['lairucremid'] = showid
templatekw.keywords['lairucremgraphnode'] = showgraphnode


cmdtable = {}
command = cmdutil.command(cmdtable)

@command('^debuglairucremgraphlog', [
    ('r', 'rev', [], i18n._('show the specified revision or range'), i18n._('REV')),
    ('T', 'template', '', i18n._('display with template'), i18n._('TEMPLATE')),
], inferrepo=True)
def debuglairucremgraphlog(ui, repo, *pats, **opts):
    '''glog equivalent for lairucrem.'''
    # This code merges cdmutil.graphlog and cmdutil.displaygraph.
    #
    # The main differences with the original code is that the working context
    # is added to the DAG
    #
    # Note that useless options like `getrenamed`, `filematcher` have
    # been removed.
    # Parameters are identical to log command ones
    revs, dummy_expr, filematcher = cmdutil.getgraphlogrevs(repo, pats, opts)
    revdag = itertools.chain(
        [(None, 'C', repo[None], [c.rev() for c in repo[None].parents()])], # workingctx
        graphmod.dagwalker(repo, revs),
    )
    getrenamed = None
    displayer = cmdutil.show_changeset(ui, repo, opts, buffered=True)
    cmdutil.displaygraph(ui, repo, revdag, displayer,
                         graphmod.asciiedges, getrenamed, filematcher)
