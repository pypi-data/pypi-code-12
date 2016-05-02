from __future__ import print_function
import click
from globus_cli.helpers import common_options

from globus_cli.services.auth.get_identities import get_identities


@click.group('auth', help=(
    'Interact with Globus Auth API. '
    'Inspect Tokens, Identities, and Identity Sets, consent to service '
    'terms, revoke and manage Consents, and manage OAuth Clients.'))
@common_options
def auth_command():
    pass


auth_command.add_command(get_identities)
