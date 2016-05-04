import click

from globus_cli.helpers import common_options

from globus_cli.services.transfer.acl import acl_command
from globus_cli.services.transfer.bookmark import bookmark_command
from globus_cli.services.transfer.endpoint import endpoint_command
from globus_cli.services.transfer.task import task_command
from globus_cli.services.transfer.async_transfer import async_transfer_command
from globus_cli.services.transfer.async_delete import async_delete_command
from globus_cli.services.transfer.ls import ls_command
from globus_cli.services.transfer.mkdir import mkdir_command
from globus_cli.services.transfer.rename import rename_command


@click.group('transfer', help=(
    'Interact with Globus Transfer API. '
    'Transfer, Delete, List, and Rename files on Endpoints, manage your '
    'Endpoints and Shares, and monitor your ongoing Transfer Tasks'))
@common_options
def transfer_command():
    pass


# subgroups
transfer_command.add_command(acl_command)
transfer_command.add_command(bookmark_command)
transfer_command.add_command(endpoint_command)
transfer_command.add_command(task_command)
# commands
transfer_command.add_command(async_transfer_command)
transfer_command.add_command(async_delete_command)
transfer_command.add_command(ls_command)
transfer_command.add_command(mkdir_command)
transfer_command.add_command(rename_command)
