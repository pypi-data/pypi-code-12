from __future__ import print_function
import click

from globus_cli.helpers import (
    outformat_is_json, common_options, print_json_response,
    colon_formatted_print)
from globus_cli.services.transfer.helpers import get_client, endpoint_id_option


@click.command('show', help='Display a detailed Endpoint definition')
@common_options
@endpoint_id_option
def endpoint_show(endpoint_id):
    """
    Executor for `globus transfer endpoint show`
    """
    client = get_client()

    res = client.get_endpoint(endpoint_id)

    if outformat_is_json():
        print_json_response(res)
    else:
        fields = (('Display Name', 'display_name'), ('ID', 'id'),
                  ('Owner', 'owner_string'), ('Activated', 'activated'),
                  ('Shareable', 'shareable'))
        colon_formatted_print(res, fields)
