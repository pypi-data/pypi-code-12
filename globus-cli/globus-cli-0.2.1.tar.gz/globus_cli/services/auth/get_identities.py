import click

from globus_cli.helpers import (
    common_options, print_json_response, outformat_is_json,
    print_table)
from globus_cli.services.auth.helpers import get_auth_client


_USERNAMES_STYLE = 'usernames'
_IDS_STYLE = 'identities'


@click.command('get-identities', help='Lookup Globus Auth Identities')
@common_options
@click.option('--usernames', 'lookup_style', default=True,
              help=('Values are Usernames to lookup in Globus Auth. '
                    'This is the default behavior'),
              flag_value=_USERNAMES_STYLE)
@click.option('--identities', 'lookup_style',
              help='Values are Identity IDs to lookup in Globus Auth',
              flag_value=_IDS_STYLE)
@click.argument('values', required=True, nargs=-1)
def get_identities(values, lookup_style):
    """
    Executor for `globus auth get-identities`
    """
    client = get_auth_client()

    params = {}

    # set commandline params if passed
    if lookup_style == _USERNAMES_STYLE:
        params['usernames'] = ','.join(values)
    elif lookup_style == _IDS_STYLE:
        params['ids'] = ','.join(values)

    res = client.get_identities(**params)

    if outformat_is_json():
        print_json_response(res)
    else:
        ids = res['identities']

        def max_keylen(key):
            return max(len(i[key]) for i in ids)

        print_table(ids, [('ID', 'id'), ('Full Name', 'name'),
                          ('Username', 'username'),
                          ('Organization', 'organization'),
                          ('Email Address', 'email')])
