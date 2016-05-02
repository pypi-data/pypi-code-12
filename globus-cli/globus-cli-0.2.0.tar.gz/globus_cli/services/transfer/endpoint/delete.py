from __future__ import print_function
import click

from globus_cli.helpers import (
    common_options, outformat_is_json, print_json_response)
from globus_cli.services.transfer.helpers import get_client, endpoint_id_option


@click.command('delete', help='Delete a given Endpoint')
@common_options
@endpoint_id_option
def endpoint_delete(endpoint_id):
    """
    Executor for `globus transfer endpoint delete`
    """
    client = get_client()

    res = client.delete_endpoint(endpoint_id)

    if outformat_is_json():
        print_json_response(res)
    else:
        print(res['message'])
