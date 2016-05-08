#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

from ec3.config import Config
from ec3 import exceptions
# from ec3.main_shell import main_shell
from ec3.main_ssh import main_ssh

FUNC_MAP = {
    'ssh': main_ssh
    # 'shell': main_shell
}

def main():
    conf = Config.create()
    command = conf.args.command
    if command not in FUNC_MAP:
        raise exceptions.InvalidInput("'%s' is not a valid command." % command)
    print('command: ', conf.args.command)
    FUNC_MAP[command](conf)
