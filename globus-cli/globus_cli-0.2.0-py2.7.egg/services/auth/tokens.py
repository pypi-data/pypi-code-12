from globus_cli.helpers import cliargs, CLIArg


@cliargs('Inspect Globus Auth Tokens',
         CLIArg('token', help='Token to lookup in Globus Auth'))
def token_introspect(args):
    """
    Executor for `globus auth token-introspect`
    """
    # client.token_introspect(token, **params)
    raise NotImplementedError('Requires Client Credential Support')
