from __future__ import print_function

from globus_cli.helpers import (
    outformat_is_json, cliargs, CLIArg, print_table, print_json_response)
from globus_cli.services.auth import (
    maybe_lookup_identity_id, lookup_identity_name)
from globus_cli.services.transfer.helpers import get_client


@cliargs('List of Access Control List rules on an Endpoint',
         CLIArg('endpoint-id', required=True, help='ID of the endpoint'))
def acl_list(args):
    """
    Executor for `globus transfer access acl-list`
    """
    client = get_client()

    rules = client.endpoint_acl_list(args.endpoint_id)

    if outformat_is_json(args):
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


@cliargs('Get detailed info on a specific ACL rule',
         CLIArg('endpoint-id', required=True, help='ID of the endpoint'),
         CLIArg('rule-id', required=True, help='ID of the rule to display'))
def show_acl_rule(args):
    """
    Executor for `globus transfer access show-acl-rule`
    """
    client = get_client()

    res = client.get_endpoint_acl_rule(args.endpoint_id, args.rule_id)

    print_json_response(res)


@cliargs('Add an ACL rule',
         CLIArg('endpoint-id', required=True, help='ID of the endpoint'),
         CLIArg('permissions', required=True, choices=('r', 'rw'),
                type=str.lower, help=('Permissions to add. '
                                      'Read-Only or Read/Write')),
         CLIArg('principal', required=True,
                help=('Principal to grant permissions to. ID of a Group or '
                      'Identity, or a valid Identity Name, like '
                      '"go@globusid.org"')),
         CLIArg('principal-type', required=True,
                choices=('identity', 'group', 'anonymous',
                         'all_authenticated_users'),
                type=str.lower, help='Principal type to grant permissions to'),
         CLIArg('path', required=True,
                help='Path on which the rule grants permissions'))
def add_acl_rule(args):
    """
    Executor for `globus transfer access add-acl-rule`
    """
    client = get_client()

    principal = args.principal
    if args.principal_type == 'identity':
        principal = maybe_lookup_identity_id(principal)

    rule_data = {
        'DATA_TYPE': 'access',
        'permissions': args.permissions,
        'principal': principal,
        'principal_type': args.principal_type,
        'path': args.path
    }

    res = client.add_endpoint_acl_rule(args.endpoint_id, rule_data)

    print_json_response(res)


@cliargs('Remove an ACL rule',
         CLIArg('endpoint-id', required=True, help='ID of the endpoint'),
         CLIArg('rule-id', required=True, help='ID of the rule to display'))
def del_acl_rule(args):
    """
    Executor for `globus transfer access del-acl-rule`
    """
    client = get_client()

    res = client.delete_endpoint_acl_rule(args.endpoint_id, args.rule_id)

    print_json_response(res)


@cliargs('Update an ACL rule',
         CLIArg('endpoint-id', required=True, help='ID of the endpoint'),
         CLIArg('rule-id', required=True, help='ID of the rule to display'),
         CLIArg('permissions', default=None, choices=('r', 'rw'),
                type=str.lower, help=('Permissions to add. '
                                      'Read-Only or Read/Write')),
         CLIArg('principal', default=None,
                help=('Principal to grant permissions to. ID of a Group or '
                      'Identity, or a valid Identity Name, like '
                      '"go@globusid.org"')),
         CLIArg('principal-type', default=None,
                choices=('identity', 'group', 'anonymous',
                         'all_authenticated_users'),
                type=str.lower, help='Principal type to grant permissions to'),
         CLIArg('path', default=None,
                help='Path on which the rule grants permissions'))
def update_acl_rule(args):
    """
    Executor for `globus transfer access update-acl-rule`
    """
    client = get_client()

    rule_data = {
        'DATA_TYPE': 'access'
    }
    for key, val in (('permissions', args.permissions),
                     ('principal', args.principal),
                     ('principal_type', args.principal_type),
                     ('path', args.path)):

        if key == 'principal':
            val = maybe_lookup_identity_id(val)

        if val is not None:
            rule_data[key] = val

    res = client.update_endpoint_acl_rule(args.endpoint_id, args.rule_id,
                                          rule_data)

    print_json_response(res)
