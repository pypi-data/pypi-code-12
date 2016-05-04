from __future__ import print_function
import click

from globus_cli.helpers import (
    common_options, outformat_is_json, print_table, print_json_response)
from globus_cli.services.auth import lookup_identity_name
from globus_cli.services.transfer.helpers import get_client, endpoint_id_option


@click.command('list', help='List of Access Control List rules on an Endpoint')
@common_options
@endpoint_id_option
def acl_list(endpoint_id):
    """
    Executor for `globus transfer acl list`
    """
    client = get_client()

    rules = client.endpoint_acl_list(endpoint_id)

    if outformat_is_json():
        print_json_response(rules)
    else:
        def principal_str(rule):
            principal = rule['principal']
            if rule['principal_type'] == 'identity':
                return lookup_identity_name(principal)
            elif rule['principal_type'] == 'group':
                return ('https://www.globus.org/app/groups/{}'
                        ).format(principal)
            return principal

        print_table(rules, [('Rule ID', 'id'), ('Permissions', 'permissions'),
                            ('Shared With', principal_str), ('Path', 'path')])
