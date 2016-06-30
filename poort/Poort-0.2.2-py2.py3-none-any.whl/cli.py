#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from os import path
from os import SEEK_END
from os import system
from os import unlink
from psutil import NoSuchProcess
from psutil import Process
from subprocess import check_call
import click
import curses
import sys

try:
    import gunicorn

    assert gunicorn
except ImportError:
    raise ValueError('Poort::cli requires Gunicorn to run!')

try:
    sys.path.append('.')
    import config
except ImportError:
    raise ValueError('Could not import `config.py`.')


@click.group()
@click.option('--debug/--no-debug', default=False)
def main(debug):
    if debug:
        click.echo('proc_name = %s' % config.proc_name)
        click.echo('bind      = %s' % config.bind)
        click.echo('pidfile   = %s' % config.pidfile)


def get_process():
    if not path.exists(config.pidfile):
        return False

    try:
        with open(config.pidfile) as stream:
            return Process(int(stream.read().strip()))
    except NoSuchProcess:
        unlink(config.pidfile)
        return False


@main.command('start')
@click.option('--package', default='app')
@click.option('--runnable', default='application')
@click.option('--environ', default='development')
@click.option('--check/--no-check', default=True)
def start(package, runnable, environ, check):
    if get_process() is not False:
        click.secho('Application is already running.', err=True, fg='red')
        raise click.Abort

    if check:
        cmd = 'python -c $\'import %s;\\nif not hasattr(%s, "%s"): exit(1)\''
        cmd = cmd % (package, package, runnable)
        msg = 'Failed to import %s:%s.' % (package, runnable)
        assert system(cmd) == 0, msg

    click.secho('Starting your application.', fg='green')
    system('ENVIRON=%s gunicorn -c config.py %s:%s' % (
        environ, package, runnable))


@main.command('stop')
@click.option('--graceful/--quick', default=True)
def stop(graceful):
    if get_process() is False:
        click.secho('Application is not running.', err=True, fg='red')
        raise click.Abort

    if graceful:
        click.secho('Stopping your application.', fg='green')
        system('kill -TERM `cat %s`' % config.pidfile)
    else:
        click.secho('Stopping your application (force-quit).', fg='purple')
        system('kill -QUIT `cat %s`' % config.pidfile)


@main.command('reload')
def reload():
    if get_process() is False:
        click.secho('Application is not running.', err=True, fg='red')
        raise click.Abort

    click.secho('Restarting application.', fg='green')
    system('kill -HUP `cat %s`' % config.pidfile)


@main.command('scale')
@click.argument('way', type=click.Choice(['up', 'down']))
@click.argument('amount', default=1)
def scale(way, amount):
    if get_process() is False:
        click.secho('Application is not running.', err=True, fg='red')
        raise click.Abort

    if amount == 0:
        click.secho('Cannot scale 0.', err=True, fg='red')
        raise click.Abort

    if way == 'down':
        click.secho('Scaling application %d down.' % amount, fg='green')
        for i in range(amount):
            system('kill -TTOU `cat %s`' % config.pidfile)
    elif way == 'up':
        click.secho('Scaling application %d up.' % amount, fg='green')
        for i in range(amount):
            system('kill -TTIN `cat %s`' % config.pidfile)


@main.command('status')
@click.option('--watch/--once', default=True)
@click.option('--delay', default=1)
def status(watch, delay):
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
            screen.addstr(1, 2, config.proc_name or 'Unnamed')
            screen.addstr(4, 2, 'Running with %d workers (default is %d)' % (
                workers, config.workers))

            screen.addstr(6, 2, '%-10s %5s   %5s   %6s' % (
                'Name', 'PID', 'CPU', 'Mem'))
            screen.addstr(7, 2, '-' * 40)

            line('Master', process, 8)

            for cx, child in enumerate(children):
                line('Worker %d' % (cx + 1), child, 9 + cx)

            usage = '(q)uit (u)pscale (d)ownscale (r)estart'

            screen.addstr(9 + workers + 2, 2, '%-20s -- %s' % (
                status, usage))

            height = screen.getmaxyx()[0] - 1

            top = 9 + workers + 5
            max_lines = height - top

            with open(config.errorlog) as stream:
                contents = tail(stream, max_lines)

            for lx, content in enumerate(contents):
                screen.addstr(top + lx, 2, content)

            char = screen.getch()
            if char != curses.ERR:
                key = chr(char)

                if key == 'q':
                    status = 'Quit'
                    running = False
                elif key == 'u':
                    status = 'Scaling up'
                    system('kill -TTIN `cat %s`' % config.pidfile)
                elif key == 'd':
                    status = 'Scaling down'
                    system('kill -TTOU `cat %s`' % config.pidfile)
                elif key == 'r':
                    status = 'Restarting'
                    system('kill -HUP `cat %s`' % config.pidfile)
                else:
                    status = 'Unknown key'
            else:
                status = 'Waiting...'

        except KeyboardInterrupt:
            running = False
        else:
            if not watch:
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
