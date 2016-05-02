from __future__ import print_function
import click

from globus_cli.helpers import (
    common_options, outformat_is_json, print_json_response)
from globus_cli.services.transfer.helpers import get_client
from globus_cli.services.transfer.activation import autoactivate


@click.command('mkdir', help='Make a directory on an Endpoint')
@common_options
@click.option('--endpoint-id', required=True, help='ID of the Endpoint')
@click.option('--path', required=True,
              help='Path on the remote Endpoint to create')
def mkdir_command(path, endpoint_id):
    """
    Executor for `globus transfer mkdir`
    """
    client = get_client()
    autoactivate(client, endpoint_id, if_expires_in=60)

    res = client.operation_mkdir(endpoint_id, path=path)

    if outformat_is_json():
        print_json_response(res)
    else:
        print(res['message'])
