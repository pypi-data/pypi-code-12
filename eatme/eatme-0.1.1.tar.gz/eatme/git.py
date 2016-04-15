# -*- coding: utf-8 -*-
import os

from plumbum import local, colors
from plumbum.commands.processes import ProcessExecutionError

git = local['git']


def pull_update(path, branch=None, *args, **kwargs):
    """git pull + git checkout"""
    git_pull = git['pull']
    git_checkout = git['checkout']

    if not os.path.exists(path):
        return

    if branch:
        git_pull = git_pull['origin', branch]
        git_checkout = git_checkout[branch]

    with colors.green:
        print(path)

    if branch:
        with colors.yellow:
            print(git_checkout)

        try:
            with local.cwd(path):
                print(git_checkout())
        except ProcessExecutionError as e:
            with colors.red:
                print(e.stderr)

            # Выходим, если была ошибка
            return

    with colors.yellow:
        print(git_pull)

    try:
        with local.cwd(path):
            print(git_pull())
    except ProcessExecutionError as e:
        with colors.red:
            print(e.stderr)


def push(path, branch=None, *args, **kwargs):
    """git push"""
    git_push = git['push', '--set-upstream', '--progress', 'origin']

    if not os.path.exists(path):
        return

    if branch:
        git_push = git_push[branch]

    with colors.green:
        print(path)

    with colors.yellow:
        print(git_push)

    try:
        with local.cwd(path):
            print(git_push())
    except ProcessExecutionError as e:
        with colors.red:
            print(e.stderr)


def branch(path):
    """Show current Git branch"""
    git_branch = git['rev-parse', '--abbrev-ref', 'HEAD']

    if not os.path.exists(path):
        return

    with colors.green:
        print(path)

    with colors.yellow:
        print(git_branch)

    try:
        with local.cwd(path):
            print(git_branch())
    except ProcessExecutionError as e:
        with colors.red:
            print(e.stderr)
