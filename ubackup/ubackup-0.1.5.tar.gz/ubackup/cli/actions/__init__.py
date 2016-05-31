import click
import pkgutil
import os
from collections import defaultdict
from ubackup.utils import memoized


@memoized
def dicover_commands():
    '''Discover commands in this module.
    Search for all submodules and find all click commands.
    Return a dict of actions/types.
    '''
    commands = defaultdict(list)
    for importer, modname, ispkg in pkgutil.iter_modules([os.path.dirname(__file__)]):
        module = __import__('ubackup.cli.actions.%s' % modname, fromlist=[''])
        for key, value in module.__dict__.items():
            if isinstance(getattr(module, key), click.core.Command):
                commands[key].append(modname)
    return commands


class Actions(click.Group):
    '''Actions are submodules click commands of this module.
    '''

    def list_commands(self, ctx):
        cmds = sorted(self.commands)
        backup_cmds = [key for key, value in dicover_commands().items()]
        return sorted(cmds + backup_cmds)

    def get_command(self, ctx, name):
        return self.commands.get(name) or Types(command_name=name)


class Types(click.MultiCommand):
    '''Types are submodules of this modules which have click commands.
    '''

    def __init__(self, command_name, *args, **kwargs):
        super(Types, self).__init__(*args, **kwargs)
        self.command_name = command_name

    def list_commands(self, ctx):
        return dicover_commands()[self.command_name]

    def get_command(self, ctx, name):
        backup_cls = __import__('ubackup.cli.actions.%s' % name, fromlist=[''])
        cmd = getattr(backup_cls, self.command_name)
        return cmd
