from __future__ import print_function
import click

from globus_cli.helpers import (
    CaseInsensitiveChoice, outformat_is_json, common_options,
    print_json_response)
from globus_cli.services.auth import maybe_lookup_identity_id
from globus_cli.services.transfer.helpers import (
    get_client, endpoint_id_option, assemble_generic_doc)


@click.command('create', help='Create a Role on an Endpoint')
@common_options
@endpoint_id_option
@click.option('--principal-type', required=True,
              type=CaseInsensitiveChoice(('identity', 'group')),
              help='Type of entity to set a role on')
@click.option('--principal', required=True,
              help=('Entity to set a role on. ID of a Group or Identity, or '
                    'a valid Identity Name, like "go@globusid.org"'))
@click.option('--role', default='access_manager', show_default=True,
              type=CaseInsensitiveChoice(('access_manager',)),
              help='A role to assign. Currently only supports access_manager')
def role_create(role, principal, principal_type, endpoint_id):
    """
    Executor for `globus transfer endpoint role show`
    """
    client = get_client()

    if principal_type == 'identity':
        principal = maybe_lookup_identity_id(principal)

    role_doc = assemble_generic_doc(
        'role', principal_type=principal_type, principal=principal,
        role=role)

    res = client.add_endpoint_role(endpoint_id, role_doc)

    if outformat_is_json():
        print_json_response(res)
    else:
        print('ID: ' + res['id'])
