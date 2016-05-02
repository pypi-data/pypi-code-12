from __future__ import print_function
import click

from globus_cli.helpers import common_options, print_table, outformat_is_json
from globus_cli.services.transfer.helpers import (
    get_client, endpoint_id_option, print_json_from_iterator)


@click.command('server-list', help='List all servers belonging to an Endpoint')
@common_options
@endpoint_id_option
def endpoint_server_list(endpoint_id):
    """
    Executor for `globus transfer endpoint server-list`
    """
    client = get_client()

    server_iterator = client.endpoint_server_list(endpoint_id)

    if outformat_is_json():
        print_json_from_iterator(server_iterator)
    else:
        print_table(server_iterator, [('URI', 'uri')])
