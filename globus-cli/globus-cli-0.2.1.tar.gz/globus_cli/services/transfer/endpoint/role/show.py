from __future__ import print_function
import click

from globus_cli.helpers import (
    outformat_is_json, common_options, print_json_response,
    colon_formatted_print)
from globus_cli.services.transfer.helpers import get_client, endpoint_id_option
from globus_cli.services.transfer.endpoint.role.helpers import role_id_option
from globus_cli.services.auth import lookup_identity_name


@click.command('show', help='Show full info for a Role on an Endpoint')
@common_options
@endpoint_id_option
@role_id_option
def role_show(role_id, endpoint_id):
    """
    Executor for `globus transfer endpoint role show`
    """
    client = get_client()

    role = client.get_endpoint_role(endpoint_id, role_id)

    if outformat_is_json():
        print_json_response(role)
    else:
        formattable_doc = {
            'principal_type': role['principal_type'],
            'principal': lookup_identity_name(role['principal']),
            'role': role['role']
        }
        named_fields = (('Principal Type', 'principal_type'),
                        ('Principal', 'principal'), ('Role', 'role'))
        colon_formatted_print(formattable_doc, named_fields)
