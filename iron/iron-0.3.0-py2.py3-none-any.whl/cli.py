import sys
from importlib import import_module
from shutil import rmtree

import click
from click import echo, pass_context

from pathlib import Path

from .commands import run_commands
from .exceptions import IronError, IronFileNotFound
from .registry import _command_registry
from .utils import IRON_TMP_ROOT
from .watchers import watch_forever


def find_ironfile():
    """
    Attempt to locate an ironfile.

    It tries to find a file named "ironfile.py" by searching parent dirs to
    the current working directory.
    """
    IRONFILE = 'ironfile.py'

    def iter_dirs():
        path = Path('.').absolute()
        yield path
        yield from path.parents

    def iter_files():
        for path in iter_dirs():
            yield path.joinpath(IRONFILE)

    tried = []
    for path in iter_files():
        if path.is_file():
            return path
        tried.append(path)

    raise IronFileNotFound('Could not find an ironfile.py. Tried: {}'.format(tried))


class add_to_load_path:
    """
    Adds a directory to the load path while the context is active, and
    restores the load path to whatever it was before the block was run.
    """
    def __init__(self, dir):
        self.dir = dir

    def __enter__(self):
        self.path_copy = sys.path[:]
        sys.path.insert(0, str(self.dir))

    def __exit__(self, *args):
        sys.path = self.path_copy[:]


def load_ironfile():
    """Finds and loads an ironfile."""
    ironfile = find_ironfile()
    dir = ironfile.parent

    # Pull a trick where we temporarily put the dir containing the ironfile on
    # the load path, then load the module, and remove it again.
    with add_to_load_path(dir):
        ironfile = import_module('ironfile')

    return ironfile


def print_usage(ctx):
    echo(ctx.get_help() + '\n')
    echo('Available commands:')
    for command in sorted(_command_registry):
        echo('  {:14s}  {}'.format(command, (_command_registry[command].__doc__ or '').strip()))
    echo('')


@click.command()
@click.option('-e', '--env', help='Target environment.', default='dev', metavar='<name>')
@click.option('-v', '--verbose', is_flag=True, help='Be verbose.')
@click.version_option()
@click.argument('commands', nargs=-1)
@pass_context
def cli(ctx, env, verbose, commands):
    load_ironfile()

    if not commands:
        print_usage(ctx)
        sys.exit(2)

    # Treat the 'watch' command special
    start_watching = 'watch' in commands
    commands = list(cmdname for cmdname in commands if cmdname != 'watch')

    # Check if all commands are known
    for cmdname in commands:
        if cmdname not in _command_registry:
            click.secho('Unknown command: "{}"'.format(cmdname), fg='red')
            sys.exit(2)

    try:
        run_commands(commands, env, verbose)

        if start_watching:
            try:
                watch_forever(env, verbose)
            except KeyboardInterrupt:
                click.echo('Stopping watcher...')
    except IronError as e:
        print(e)
    else:
        # Clean up temporary directory, if available
        if Path(IRON_TMP_ROOT).is_dir():
            rmtree(IRON_TMP_ROOT, ignore_errors=True)


if __name__ == '__main__':
    cli()
