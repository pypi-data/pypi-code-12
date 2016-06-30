#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from os import path
from os import SEEK_END
from os import system
from os import unlink
from psutil import NoSuchProcess
from psutil import Process
import click
import curses
import importlib
import sys

try:
    import gunicorn

    assert gunicorn
except ImportError:
    raise ValueError('Poort::cli requires Gunicorn to run!')

_config = None


def config():
    global _config

    if _config is None:
        try:
            sys.path.append('.')
            _config = importlib.import_module('config')
        except ImportError:
            raise ValueError('Could not import `config.py`.')

    return _config


@click.group()
@click.option('--debug/--no-debug', default=False)
def main(debug):
    if debug:
        click.echo('proc_name = %s' % config().proc_name)
        click.echo('bind      = %s' % config().bind)
        click.echo('pidfile   = %s' % config().pidfile)


def get_process():
    if not path.exists(config().pidfile):
        return False

    try:
        with open(config().pidfile) as stream:
            return Process(int(stream.read().strip()))
    except NoSuchProcess:
        unlink(config().pidfile)
        return False


@main.command('start')
@click.option('--package', default='app')
@click.option('--runnable', default='application')
@click.option('--environ', default='development')
@click.option('--check/--no-check', default=True)
def start(package, runnable, environ, check):
    """Start a server for your app.

    :param package: Package/module containing your app.
    :param runnable: Entrypoint of the server for requests.
    :param environ: Which environment to start
        (production, staging, development [default]).
    :param check: Check if the package is importable and the entrypoint is
        runnable.

    :type package: str
    :type runnable: str
    :type environ: str
    :type check: bool

    .. code-block:: bash

        poort start --environ production
        poort status

    """
    if get_process() is not False:
        click.secho('Application is already running.', err=True, fg='red')
        raise click.Abort

    if check:
        cmd = 'python -c \'import %s; exit(0 if hasattr(%s, "%s") else 1)\''
        cmd = cmd % (package, package, runnable)
        msg = 'Failed to import %s:%s.' % (package, runnable)
        assert system(cmd) == 0, msg

    click.secho('Starting your application.', fg='green')
    system('ENVIRON=%s gunicorn -c config.py %s:%s' % (
        environ, package, runnable))


@main.command('stop')
@click.option('--graceful/--quick', default=True)
def stop(graceful):
    """Stop the server.

    :param graceful: Graceful or forceful (--quick).

    :type graceful: bool

    .. code-block:: bash

        poort stop

    """
    if get_process() is False:
        click.secho('Application is not running.', err=True, fg='red')
        raise click.Abort

    if graceful:
        click.secho('Stopping your application.', fg='green')
        system('kill -TERM `cat %s`' % config().pidfile)
    else:
        click.secho('Stopping your application (force-quit).', fg='purple')
        system('kill -QUIT `cat %s`' % config().pidfile)


@main.command('reload')
def reload():
    """Reload the server.

    .. code-block:: bash

        poort reload

    """
    if get_process() is False:
        click.secho('Application is not running.', err=True, fg='red')
        raise click.Abort

    click.secho('Restarting application.', fg='green')
    system('kill -HUP `cat %s`' % config().pidfile)


@main.command('scale')
@click.argument('way', type=click.Choice(['up', 'down']))
@click.argument('amount', default=1)
def scale(way, amount):
    """Scale the workers of server up or down.

    :param way: Which way to scale (--way up | --way down)
    :param amount: The amount of workers to scale.

    :type way: str
    :type amount: int

    .. code-block:: bash

        poort scale --way up --amount 2

    """
    if get_process() is False:
        click.secho('Application is not running.', err=True, fg='red')
        raise click.Abort

    if amount == 0:
        click.secho('Cannot scale 0.', err=True, fg='red')
        raise click.Abort

    if way == 'down':
        click.secho('Scaling application %d down.' % amount, fg='green')
        for i in range(amount):
            system('kill -TTOU `cat %s`' % config().pidfile)
    elif way == 'up':
        click.secho('Scaling application %d up.' % amount, fg='green')
        for i in range(amount):
            system('kill -TTIN `cat %s`' % config().pidfile)


@main.command('status')
@click.option('--delay', default=1)
def status(delay):
    """Show a status screen (refreshing) of the server.

    The status screen shows information about the workers and gives you
    some shortcut keys to handle the server (quit, upscale, download, reload).
    It also shows the last couple of lines from the server error log.

    :param watch: Keep watching
    :param amount: The amount of workers to scale.

    :type way: str
    :type amount: int

    .. code-block:: bash

        poort status

    Output example::

          test-poort-two


          Running with 2 workers (default is 2)

          Name         PID     CPU      Mem
          ----------------------------------------
          Master     27309    0.0%     8.1M
          Worker 1   27316    0.3%    36.8M
          Worker 2   27319    0.3%    36.6M


          Waiting...           -- (q)uit (u)pscale (d)ownscale (r)eload


          [2016-06-30 13:54:13] [26806] [INFO] Worker exiting (pid: 26806)
          [2016-06-30 13:54:13] [26805] [INFO] Worker exiting (pid: 26805)
          [2016-06-30 13:54:13] [26831] [INFO] Booting worker with pid: 26831
          [2016-06-30 13:54:13] [26832] [INFO] Booting worker with pid: 26832

    .. warning::

        This is a very curde program, do not mash a key!

    """
    if get_process() is False:
        click.secho('Application is not running.', err=True, fg='red')
        raise click.Abort

    process = get_process()
    if not process:
        click.secho('Application is not running.', err=True, fg='red')
        raise click.Abort

    screen = curses.initscr()
    curses.halfdelay(delay * 10)
    curses.noecho()

    def line(name, proc, y, x=2):
        cpu_percentage = proc.cpu_percent(None)
        memory = proc.memory_info()

        screen.addstr(y, x, '%-10s %5.d   %4.1f%%   %5.1fM' % (
            name, proc.pid,
            cpu_percentage, memory.rss / 1024 / 1024))

    status = 'Waiting...'

    running = True
    while running:
        try:
            children = process.children()
            workers = len(children)

            screen.erase()
            screen.addstr(1, 2, config().proc_name or 'Unnamed')
            screen.addstr(4, 2, 'Running with %d workers (default is %d)' % (
                workers, config().workers))

            screen.addstr(6, 2, '%-10s %5s   %5s   %6s' % (
                'Name', 'PID', 'CPU', 'Mem'))
            screen.addstr(7, 2, '-' * 40)

            line('Master', process, 8)

            for cx, child in enumerate(children):
                line('Worker %d' % (cx + 1), child, 9 + cx)

            usage = '(q)uit (u)pscale (d)ownscale (r)eload'

            screen.addstr(9 + workers + 2, 2, '%-20s -- %s' % (
                status, usage))

            y, x = screen.getmaxyx()
            height = y - 1

            top = 9 + workers + 5
            max_lines = height - top

            with open(config().errorlog) as stream:
                contents = tail(stream, max_lines)

            for lx, content in enumerate(contents):
                screen.addstr(top + lx, 2, content[:x - 4])

            char = screen.getch()
            if char != curses.ERR:
                key = chr(char)

                if key == 'q':
                    status = 'Quit'
                    running = False
                elif key == 'u':
                    status = 'Scaling up'
                    system('kill -TTIN `cat %s`' % config().pidfile)
                elif key == 'd':
                    status = 'Scaling down'
                    system('kill -TTOU `cat %s`' % config().pidfile)
                elif key == 'r':
                    status = 'Restarting'
                    system('kill -HUP `cat %s`' % config().pidfile)
                else:
                    status = 'Unknown key'
            else:
                status = 'Waiting...'

        except KeyboardInterrupt:
            running = False

    curses.endwin()


def tail(f, lines=1, _buffer=4098):
    """Tail a file and get X lines from the end"""
    # place holder for the lines found
    lines_found = []

    # block counter will be multiplied by buffer
    # to get the block size from the end
    block_counter = -1

    # loop until we find X lines
    while len(lines_found) < lines:
        try:
            f.seek(block_counter * _buffer, SEEK_END)
        except IOError:  # too small or too many lines requested
            f.seek(0)
            lines_found = f.readlines()
            break

        lines_found = f.readlines()

        if len(lines_found) > lines:
            break

        block_counter -= 1

    return lines_found[-lines:]
