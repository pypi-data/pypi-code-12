# -*- coding: utf-8 -*-
from plumbum import local, colors
from plumbum.commands.processes import ProcessExecutionError


def pull_update(path, branch=None, clean=False):
    """hg pull + hg update"""
    hg = local['hg']
    hg = hg['--repository', path]
    hg_pull = hg['pull']
    hg_update = hg['update']

    if clean is True:
        hg_update = hg_update['--clean']

    if branch:
        # Кавычки нужны для полного отображения имени бранча в тексте ошибки
        hg_update = hg_update['--rev', '\'%s\'' % branch]

    with colors.green:
        print(path)

    with colors.yellow:
        print(hg_pull)

    try:
        print(hg_pull())
    except ProcessExecutionError as e:
        with colors.red:
            print(e.stderr)

    with colors.yellow:
        print(hg_update)

    try:
        # Игнорируем ошибки:
        # 0 - changesets found
        print(hg_update(retcode=[0]))
    except ProcessExecutionError as e:
        # Остальные отлавливаем
        with colors.red:
            print(e.stderr)


def push(path, branch=None, new_branch=True):
    """hg push"""
    hg = local['hg']
    hg = hg['--repository', path]

    hg_push = hg['push']

    if branch:
        hg_push = hg_push['--branch', branch]

    if new_branch is True:
        hg_push = hg_push['--new-branch']

    with colors.green:
        print(path)

    with colors.yellow:
        print(hg_push)

    try:
        # Игнорируем ошибки:
        # 0 - changesets found
        # 1 - no changes found
        print(hg_push(retcode=[0, 1]))
    except ProcessExecutionError as e:
        # Остальные отлавливаем
        with colors.red:
            print(e.stderr)


def status(path):
    """hg status"""
    hg = local['hg']
    hg = hg['--repository', path]

    hg_status = hg['status']

    with colors.green:
        print(path)

    with colors.yellow:
        print(hg_status)

    try:
        print(hg_status())
    except ProcessExecutionError as e:
        with colors.red:
            print(e.stderr)


def branch(path):
    """hg branch"""
    hg = local['hg']
    hg = hg['--repository', path]

    hg_branch = hg['branch']

    with colors.green:
        print(path)

    with colors.yellow:
        print(hg_branch)

    try:
        print(hg_branch())
    except ProcessExecutionError as e:
        with colors.red:
            print(e.stderr)
