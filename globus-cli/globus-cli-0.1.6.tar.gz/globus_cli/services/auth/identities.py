from globus_cli.helpers import cliargs, CLIArg, print_json_response
from globus_cli.services.auth.helpers import get_auth_client


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
    client = get_auth_client()

    params = {}

    # set commandline params if passed
    if args.usernames:
        params['usernames'] = ','.join(args.usernames)
    if args.identities:
        params['ids'] = ','.join(args.usernames)

    res = client.get_identities(**params)

    print_json_response(res)
