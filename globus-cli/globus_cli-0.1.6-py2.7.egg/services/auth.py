import json
from globus_sdk import AuthClient

from globus_cli import version
from globus_cli.helpers import cliargs, CLIArg


def _get_auth_client():
    client = AuthClient(app_name=version.app_name)
    return client


def _validate_get_identities_args(args, parser):
    if args.usernames == [] and args.identities == []:
        parser.error('get-identities requires either --usernames or '
                     '--identities')


@cliargs('Inspect Globus Auth Identities',
         CLIArg('usernames', default=[], nargs='+',
                help='Usernames to lookup in Globus Auth'),
         CLIArg('identities', default=[], nargs='+',
                help='Identity IDs to lookup in Globus Auth'),
         arg_validator=_validate_get_identities_args)
def get_identities(args):
    """
    Executor for `globus auth get-identities`
    """
    client = _get_auth_client()

    params = {}

    # set commandline params if passed
    if args.usernames:
        params['usernames'] = ','.join(args.usernames)
    if args.identities:
        params['ids'] = ','.join(args.usernames)

    res = client.get_identities(**params)

    print(json.dumps(res.data, indent=2))


@cliargs('Inspect Globus Auth Tokens',
         CLIArg('token', help='Token to lookup in Globus Auth'))
def token_introspect(args):
    """
    Executor for `globus auth token-introspect`
    """
    raise NotImplementedError('Requires Client Credential Support')
    """
    client = AuthClient()

    params = {}

    token = config.get_auth_token(client.environment)

    res = client.token_introspect(token, **params)

    print(res.text_body)
    """
