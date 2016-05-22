#########################################################################
#  The MIT License (MIT)
#
#  Copyright (c) 2014~2015 CIVA LIN (林雪凡)
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files
#  (the "Software"), to deal in the Software without restriction, including
#  without limitation the rights to use, copy, modify, merge, publish,
#  distribute, sublicense, and/or sell copies of the Software, and to
#  permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#  CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##########################################################################


import configparser
import pathlib
import sys
import os
import signal
import os.path
import functools
import shlex
import re

from . import defaultconfig


def register_signal_handler():
    def signal_handler(signal, frame):
        print()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)


def get_rootdir_from_parents(current_dir):
    paths = [path for path in current_dir.glob('.loli')]
    if len(paths) == 1 and paths[0].is_dir():
        return current_dir
    else:
        if current_dir != current_dir.parent:
            return get_rootdir_from_parents(current_dir.parent)
        else:
            return None


def get_user_lolikitrc_path():
    user_lolikitrc = pathlib.Path(
        os.path.expanduser('~')) / '.lolikitrc'
    return user_lolikitrc


def get_project_lolikitrc_path(rootdir):
    project_lolikitrc = rootdir / '.loli' / 'lolikitrc'
    return project_lolikitrc


def get_config(rootdir=None):
    def read_config(rootdir):
        config = configparser.ConfigParser()
        config.read_dict(defaultconfig.DEFAULT_CONFIG)
        user_lolikitrc = get_user_lolikitrc_path()
        if user_lolikitrc.is_file():
            config.read(str(user_lolikitrc))
        if rootdir is not None:
            project_lolikitrc = get_project_lolikitrc_path(rootdir)
            if project_lolikitrc.is_file():
                config.read(str(project_lolikitrc))
        return config

    def expand_config(config):
        config['project']['ignore_patterns'] += (
            '\n^\\.loli($|' + ('\\\\' if os.sep == '\\' else os.sep) + ')')
        return config

    config = read_config(rootdir)
    config = expand_config(config)
    return config


def get_rootdir(config):
    def get_default_rootdir():
        default_project = pathlib.Path(
            os.path.expanduser(config['user'].get('default_project')))
        return get_rootdir_from_parents(default_project)

    current_dir = pathlib.Path(os.getcwd())
    rootdir = get_rootdir_from_parents(current_dir)
    if rootdir is None:
        rootdir = get_default_rootdir()
    return rootdir


def confirm(message):
    answer = input(message)
    if answer.lower() in ('y', 'yes'):
        return True
    else:
        return False


def get_default_opener():
    if sys.platform.startswith('linux'):
        return 'xdg-open'
    elif sys.platform.startswith('darwin'):
        return 'open'
    elif sys.platform.startswith('win'):
        return 'cmd /c \'{path}\''


@functools.lru_cache(maxsize=None)
def is_rmd(path, rootdir, ignore_patterns):
    """test the path is a resourced md path or not"""
    if all((
        path.is_file(),
        path.match('*.md'),
        all(False for p2 in path.parent.rglob('*.md') if p2 != path),
        any(True for p2
            in filted_ignore(get_resource_paths(path),
                             rootdir, ignore_patterns)),
            )):
        return True
    else:
        return False


@functools.lru_cache(maxsize=None)
def get_resource_paths(rmd_path):
    """get a list of resource file paths of a resourced md"""
    return [path for path in rmd_path.parent.glob('*')
            if path != rmd_path and path.is_file()]


def get_opener_command(opener, path):
    path = str(path)
    if ' ' in opener:
        command = shlex.split(opener)
        command = [part.format(path=path)
                   for part in command]
    else:
        command = [opener, path]
    return command


def filted_ignore(paths, rootdir, ignore_patterns):
    @functools.lru_cache(maxsize=None)
    def get_ignore_progs(ignore_patterns):
        ignore_progs = [
            re.compile(pattern.strip()) for pattern
            in ignore_patterns.split('\n')
            if pattern.strip()]
        return ignore_progs

    ignore_progs = get_ignore_progs(ignore_patterns)
    return [path for path in paths
            if not any(
                prog.search(str(path.relative_to(rootdir)))
                for prog in ignore_progs)]
