# Copyright (C) 2015 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/

import os
from mercurial import cmdutil, commands, util
import time

cmdtable = {}
command = cmdutil.command(cmdtable)

_ = str

@command('^say', [], 'WORDS')
def say(ui, repo, *pats, **opts):
    '''reapeat'''
    ui.write(str(pats[0]))
    ui.flush()

    
@command('^sleep', [], 'DURATION')
def sleep(ui, repo, *pats, **opts):
    duration = int(pats[0])
    ui.write('sleep for %is' % duration)
    ui.flush()
    time.sleep(duration)
    ui.write('awake after %is' % duration)
    ui.flush() 


@command('^mkcset',
    [('A', 'addremove', None,
     _('mark new/missing files as added/removed before committing')),
    ('', 'close-branch', None,
     _('mark a branch head as closed')),
    ('', 'amend', None, _('amend the parent of the working directory')),
    ('s', 'secret', None, _('use the secret phase for committing')),
    ('e', 'edit', None, _('invoke editor on commit messages')),
    ('i', 'interactive', None, _('use interactive mode')),
    ] + commands.walkopts + commands.commitopts + commands.commitopts2 + commands.subrepoopts,
    _('[OPTION]... [FILE]...'))
def mkcset(ui, repo, *pats, **opts):
    filename = pats[0]
    content = pats[-1] # same as filename by default
    filepath = os.path.join(repo.root, filename)
    with open(filepath, 'w') as fid:
        fid.write(content)
    commands.add(ui, repo, filepath)
    if 'message' not in opts or not opts['message']:
        opts['message'] = content
    commands.commit(ui, repo, filepath, **opts)
    ui.write('%s:%s' % (repo['.'].rev(), repo['.'].hex()))
