from __future__ import print_function
import click

from globus_cli.excepthook import set_excepthook
from globus_cli.list_commands import list_commands
from globus_cli.helpers import common_options

from globus_cli.services.auth import auth_command
from globus_cli.services.transfer import transfer_command


# there is a single global object for all click contexts, a shared dict
_global_click_obj = {}


@click.command('login', short_help='Show Login Help for the CLI',
               help=('Get authentication credentials for the Globus CLI. '
                     'Necessary before any Globus CLI commands which require '
                     'authentication will work'))
@common_options
def login_help():
    print('\nTo login to the Globus CLI, go to\n')
    print('    https://tokens.globus.org/\n')
    print('and select the the "Globus CLI" option.\n')


@click.group('globus', context_settings=dict(obj=_global_click_obj))
@common_options
def main():
    set_excepthook()


main.add_command(auth_command)
main.add_command(transfer_command)
main.add_command(login_help)
main.add_command(list_commands)
