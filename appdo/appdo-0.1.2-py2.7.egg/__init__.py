#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Main file for appdo
'''

import re
from os import execvp, path
from getpass import getuser

import click
import toml


class Config(object):
    '''
    Config
    '''

    def __init__(self, config=None):
        '''
        init
        '''
        self.config = {}
        if config:
            self.merge_config(config)

    def merge_config_file(self, conf_file):
        '''
        Merge config from file name.
        '''
        fd = open(conf_file)
        conf = toml.loads(fd.read())
        fd.close()
        return self.merge_config(conf)

    def merge_config(self, conf):
        '''
        Merge config.
        TODO: use better merging
        '''
        self.config.update(conf)

    @staticmethod
    def build_source_commands(conf):
        '''
        private method
        '''
        try:
            srcfile = conf['source']
            if isinstance(srcfile, str):
                return ['source ' + srcfile]
            else:
                return ['source ' + x for x in srcfile]
        except KeyError:
            return []

    @staticmethod
    def build_before_commands(conf):
        '''
        private method
        '''
        try:
            cmd = conf['before']
            if isinstance(cmd, str):
                return [cmd]
            else:
                return cmd
        except KeyError:
            return []

    @staticmethod
    def build_envs(conf):
        '''
        private method
        '''
        try:
            envs = conf['env']
            if isinstance(envs, dict):
                return [k + '=' + v for k,v in envs.items()]
            else:
                return []
        except KeyError:
            return []

    @staticmethod
    def build_prefix_command(conf):
        '''
        private method
        '''
        try:
            cmd = conf['prefix']
            if isinstance(cmd, str):
                return [cmd + ' ']
            else:
                return []
        except KeyError:
            return []

    def get_statements(self, mode='default'):
        '''
        Create bash statements from config file.
        returns array.
        '''
        beforerun = []
        prerun = []

        if mode in self.config.keys():
            conf = self.config[mode]
            beforerun += self.build_source_commands(conf)
            beforerun += self.build_before_commands(conf)
            prerun += self.build_envs(conf)
            prerun += self.build_prefix_command(conf)

        return beforerun, prerun


class CommandBuilder(object):
    '''
    Command Builder
    '''
    def __init__(self, args, prerun=()):
        '''
        init
        '''
        if len(args) == 1:
            args = list(args[0].split(' '))
        else:
            args = list(args)
        self.command = args
        self.beforerun = prerun[0]
        self.prerun = prerun[1]

    def build_beforerun_command(self):
        '''
        build
        '''
        if self.beforerun:
            cmd = '; '.join(self.beforerun) + '; '
        else:
            cmd = ''
        return cmd

    def build_pre_command(self):
        '''
        build
        '''
        if self.prerun:
            cmd = ' '.join(self.prerun) + ' '
        else:
            cmd = ''
        return cmd

    def build_last_command(self):
        '''
        build
        '''
        if self.command:
            cmd = ' '.join(self.command)
        return cmd

    def build_command(self):
        '''
        create bash oneliner command
        '''
        cmd = self.build_beforerun_command()
        cmd += self.build_pre_command()
        cmd += self.build_last_command()
        full_command = ['bash', '-c', cmd]
        return full_command

    def run(self):
        '''
        run the command.
        be itself
        '''
        cmd = self.build_command()
        execvp(cmd[0], cmd)


def matches(key, val, regex):
    '''
    check if it matches
    '''
    if regex:
        reg = re.compile(val)
        return key and reg.search(key)
    else:
        return key and key == val


def get_config():
    '''
    search for config files
    '''
    files = ['/etc/appdo.conf', homedir() + '/.appdo.conf']
    conf = Config()
    for filename in files:
        if path.exists(filename):
            conf.merge_config_file(filename)
    return conf


def homedir():
    '''
    return $HOME.
    just in case it be used in sudo.
    '''
    return path.expanduser('~' + getuser())


@click.command()
@click.argument('cmd', nargs=-1)
def run(cmd):
    '''
    main function
    '''
    conf = get_config()
    command = CommandBuilder(cmd, conf.get_statements())
    command.run()

