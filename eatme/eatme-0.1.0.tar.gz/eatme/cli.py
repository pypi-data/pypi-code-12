#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
from collections import namedtuple
from functools import wraps

from plumbum import colors, cli
from plumbum.cli import SwitchAttr

from eatme import __version__, __date__
from eatme import hg, git

VersionControlSystem = namedtuple('VersionControlSystem', ['GIT', 'HG'])
VCS = VersionControlSystem(
    GIT='GIT',
    HG='HG',
)

COMMANDS = {
    'pull_update': {
        VCS.HG: hg.pull_update,
        VCS.GIT: git.pull_update,
    },
    'push': {
        VCS.HG: hg.push,
        VCS.GIT: git.push,
    },
    'status': {
        VCS.HG: hg.status,
    },
    'branch': {
        VCS.HG: hg.branch,
    }

}


def print_time_spent(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        finish = time.time()
        with colors.cyan:
            print('Done in {} sec'.format(finish - start))
        return result

    return wrapper


def get_repos(start_path='.'):
    for dir_path, subdir_list, file_list in os.walk(start_path):
        if '.hg' in subdir_list:
            yield VCS.HG, dir_path

        if '.git' in subdir_list:
            yield VCS.GIT, dir_path

        # Удаляем скрытые директории из списка, чтобы не проходить по ним
        subdir_list[:] = [d for d in subdir_list if not d[0] == '.']


def run_for_all_repos(command, options=None, start_path='.'):
    options = options or {}
    for vcs, repo_path in get_repos(start_path):
        func = COMMANDS.get(command, {}).get(vcs)
        if callable(func):
            func(path=repo_path, **options)


class EatMe(cli.Application):
    PROGNAME = 'eatme'
    VERSION = '%s (%s)' % (__version__, __date__)

    def main(self, *args):
        if args:
            with colors.red:
                print "Unknown command %r" % (args[0],)
            print "=" * 20
            self.help()
            return 1  # error exit code
        if not self.nested_command:  # will be ``None`` if no sub-command follows
            with colors.red:
                print "No command given"
            print "=" * 20
            self.help()
            return 1  # error exit code


@EatMe.subcommand("push")
class Push(cli.Application):
    new_branch = cli.Flag(["--new-branch"], help="hg push --new-branch")
    branch = SwitchAttr(["-b", "--branch"], argtype=str, help="hg update --rev BRANCH")

    @print_time_spent
    def main(self, *args):
        run_for_all_repos('push', options=dict(branch=self.branch, new_branch=self.new_branch))


@EatMe.subcommand("update")
class Update(cli.Application):
    clean = cli.Flag(["-C", "--clean"], help="hg update --clean")
    branch = SwitchAttr(["-b", "--branch"], argtype=str, help="hg update --rev BRANCH")

    @print_time_spent
    def main(self, *args):
        branch = None
        if self.branch:
            branch = self.branch
        elif args:
            branch = args[0]

        run_for_all_repos('pull_update', options=dict(branch=branch, clean=self.clean))


@EatMe.subcommand("status")
class Status(cli.Application):
    @print_time_spent
    def main(self, *args):
        run_for_all_repos('status')


@EatMe.subcommand("branch")
class Branch(cli.Application):
    @print_time_spent
    def main(self, *args):
        run_for_all_repos('branch')
