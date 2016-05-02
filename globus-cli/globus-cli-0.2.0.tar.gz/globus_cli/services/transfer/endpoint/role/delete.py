from __future__ import print_function
import click

from globus_cli.helpers import (
    outformat_is_json, common_options, print_json_response)
from globus_cli.services.transfer.helpers import get_client, endpoint_id_option
from globus_cli.services.transfer.endpoint.role.helpers import role_id_option


@click.command('delete', help='Remove a Role from an Endpoint')
@common_options
@endpoint_id_option
@role_id_option
def role_delete(role_id, endpoint_id):
    """
    Executor for `globus transfer endpoint role delete`
    """
    client = get_client()

    res = client.delete_endpoint_role(endpoint_id, role_id)

    if outformat_is_json():
        print_json_response(res)
    else:
        print(res['message'])
