from __future__ import print_function
import copy
import click


@click.command('list-commands', short_help='List all CLI Commands',
               help=('List all Globus CLI Commands with short help output. '
                     'For full command help, run the command with the '
                     '`--help` flag'))
def list_commands():
    def _print_cmd(command):
        # print commands with help -- for now, we figure that no command name
        # is more than 16 chars
        print('    {:16}{}'.format(command.name, command.short_help))

    def _print_cmd_group(command, parent_names):
        parents = ' '.join(parent_names)
        if parents:
            parents = parents + ' '
        print('\n=== {}{} ===\n'.format(parents, command.name))

    def _recursive_list_commands(command, parent_names=None):
        if parent_names is None:
            parent_names = []

        # names of parent commands, including this one, for passthrough to
        # recursive calls
        new_parent_names = copy.copy(parent_names) + [command.name]

        # group-style commands are printed as headers
        if isinstance(command, click.MultiCommand):
            _print_cmd_group(command, parent_names)

            # get the set of subcommands and recursively print all of them
            group_cmds = [v for v in command.commands.values()
                          if isinstance(v, click.MultiCommand)]
            func_cmds = [v for v in command.commands.values()
                         if v not in group_cmds]
            # we want to print them all, but func commands first
            for cmd in (func_cmds + group_cmds):
                _recursive_list_commands(cmd, parent_names=new_parent_names)

        # individual commands are printed solo
        else:
            _print_cmd(command)

    # get the root context (the click context for the entire CLI tree)
    root_ctx = click.get_current_context().find_root()

    _recursive_list_commands(root_ctx.command)
    # get an extra newline at the end
    print()
