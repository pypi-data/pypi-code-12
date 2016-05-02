from __future__ import print_function
import click

from globus_cli.helpers import common_options, outformat_is_json
from globus_cli.services.transfer.helpers import (
    get_client, endpoint_id_option, print_json_from_iterator,
    endpoint_list_to_text)


@click.command(
    'my-shared-endpoint-list',
    help='List all Shared Endpoints on an Endpoint by the current user')
@common_options
@endpoint_id_option
def my_shared_endpoint_list(endpoint_id):
    """
    Executor for `globus transfer endpoint my-shared-endpoint-list`
    """
    client = get_client()

    ep_iterator = client.my_shared_endpoint_list(endpoint_id)

    if outformat_is_json():
        print_json_from_iterator(ep_iterator)
    else:
        endpoint_list_to_text(ep_iterator)
