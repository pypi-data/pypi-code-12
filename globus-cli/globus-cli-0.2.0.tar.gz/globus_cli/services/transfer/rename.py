from __future__ import print_function
import click

from globus_cli.helpers import (
    common_options, outformat_is_json, print_json_response)
from globus_cli.services.transfer.helpers import get_client, endpoint_id_option
from globus_cli.services.transfer.activation import autoactivate


@click.command('rename', help='Rename a file or directory on an Endpoint')
@common_options
@endpoint_id_option
@click.option('--old-path', required=True,
              help='Path to the file/dir to rename')
@click.option('--new-path', required=True,
              help='Desired location of the file/dir after rename')
def rename_command(new_path, old_path, endpoint_id):
    """
    Executor for `globus transfer rename`
    """
    client = get_client()
    autoactivate(client, endpoint_id, if_expires_in=60)

    res = client.operation_rename(endpoint_id, oldpath=old_path,
                                  newpath=new_path)

    if outformat_is_json():
        print_json_response(res)
    else:
        print(res['message'])
