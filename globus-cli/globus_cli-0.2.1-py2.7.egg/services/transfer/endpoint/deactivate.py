from __future__ import print_function
import click

from globus_cli.helpers import common_options, print_json_response
from globus_cli.services.transfer.helpers import get_client, endpoint_id_option


@click.command('deactivate', help='Deactivate an Endpoint')
@common_options
@endpoint_id_option
def endpoint_deactivate(endpoint_id):
    """
    Executor for `globus transfer endpoint deactivate`
    """
    client = get_client()
    res = client.endpoint_deactivate(endpoint_id)
    print_json_response(res)
