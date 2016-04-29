# -*- coding: utf-8 -*-
"""Facade over fabric.api, for env.dryrun support, and printing run/sudo commands"""
from __future__ import unicode_literals

import os
import sys
import re
import yaml
from contextlib import contextmanager
from fabric import colors
from fabric.api import *
# fabex overrides
from fabric.api import (run as fab_run, sudo as fab_sudo, cd as fab_cd, prefix as fab_prefix)

__all__ = ['print_command', 'run', 'sudo', 'cd', 'prefix']

_prefix_stack = []
_cd_stack = []

# if tty, use colors
if sys.stdout.isatty():
    red, green, blue, magenta = colors.red, colors.green, colors.blue, colors.magenta
else:
    red = green = blue = magenta = lambda x: x

def print_command(command, arrow_out=True):
    """Loudly display command with colors"""

    arrow = " ->" if arrow_out else " <-"
    pre = []
    if _cd_stack:
        pre.append(_cd_stack[-1])
    if _prefix_stack:
        pre.extend(_prefix_stack)
    if pre:
        pre.append('')
    pres = ' && '.join(pre)
    if 'role' in env:
        print("[{}:{}] $ {}{}{}".format(blue(env.host), blue(env.role), green(pres),
                                        green(command), arrow))
    else:
        print("[{}] $ {}{}{}".format(blue(env.host), green(pres), green(command), arrow))

def run(command, **kwargs):
    __doc__ = fab_run.__doc__

    if env.dryrun:
        print_command(command)
        return "[{} output]".format(command)
    to_hide = [] if env.verbose else ['running', 'output']
    with hide(*to_hide):
        return fab_run(command, **kwargs)

def sudo(command, **kwargs):
    __doc__ = fab_sudo.__doc__

    if env.dryrun:
        print_command(command)
        return "[{} output]".format(command)
    to_hide = [] if env.verbose else ['running', 'output']
    with hide(*to_hide):
        return fab_sudo(command, **kwargs)

@contextmanager
def prefix(command):
    __doc__ = fab_prefix.__doc__
    if env.dryrun:
        _prefix_stack.append(command)
        yield
        _prefix_stack.pop()
    else:
        with fab_prefix(command):
            yield

@contextmanager
def cd(path):
    __doc__ = fab_cd.__doc__
    if env.dryrun:
        _cd_stack.append(path)
        yield
        _cd_stack.pop()
    else:
        with fab_cd(path):
            yield

