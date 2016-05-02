from __future__ import print_function
import click

from globus_cli.helpers import (
    CaseInsensitiveChoice, common_options, print_json_response)
from globus_cli.services.transfer.helpers import (
    get_client, endpoint_id_option, assemble_generic_doc)
from globus_cli.services.auth import maybe_lookup_identity_id


@click.command('update-rule', help='Update an ACL rule')
@common_options
@endpoint_id_option
@click.option('--rule-id', required=True, help='ID of the rule to modify')
@click.option('--permissions', required=True,
              type=CaseInsensitiveChoice(('r', 'rw')),
              help='Permissions to add. Read-Only or Read/Write')
@click.option('--principal', required=True,
              help=('Principal to grant permissions to. ID of a Group or '
                    'Identity, or a valid Identity Name, like '
                    '"go@globusid.org"'))
@click.option('--principal-type', required=True,
              type=CaseInsensitiveChoice(('identity', 'group', 'anonymous',
                                          'all_authenticated_users')),
              help='Principal type to grant permissions to')
@click.option('--path', required=True,
              help='Path on which the rule grants permissions')
def update_acl_rule(path, principal_type, principal, permissions,
                    rule_id, endpoint_id):
    """
    Executor for `globus transfer access update-acl-rule`
    """
    client = get_client()

    rule_data = assemble_generic_doc(
        'access', permissions=permissions,
        principal=maybe_lookup_identity_id(principal),
        principal_type=principal_type, path=path)

    res = client.update_endpoint_acl_rule(endpoint_id, rule_id,
                                          rule_data)

    print_json_response(res)
