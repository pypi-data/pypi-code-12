from __future__ import print_function
import click

from globus_cli.helpers import common_options, print_json_response
from globus_cli.services.transfer.activation import autoactivate
from globus_cli.services.transfer.helpers import get_client, endpoint_id_option


@click.command('autoactivate', help='Activate an Endpoint via autoactivation')
@common_options
@endpoint_id_option
def endpoint_autoactivate(endpoint_id):
    """
    Executor for `globus transfer endpoint autoactivate`
    """
    client = get_client()
    res = autoactivate(client, endpoint_id)
    print_json_response(res)
