from globus_sdk import AuthClient

from globus_cli import version
from globus_cli.helpers import is_valid_identity_name


def get_auth_client():
    client = AuthClient(app_name=version.app_name)
    return client


def _lookup_identity_field(id_name=None, id_id=None, field='id'):
    assert (id_name or id_id) and not (id_name and id_id)
    client = get_auth_client()

    if id_name:
        kw = {'usernames': id_name}
    else:
        kw = {'ids': id_id}

    return client.get_identities(**kw)['identities'][0][field]


def maybe_lookup_identity_id(identity_name):
    if is_valid_identity_name(identity_name):
        return _lookup_identity_field(id_name=identity_name)
    else:
        return identity_name


def lookup_identity_name(identity_id):
    return _lookup_identity_field(id_id=identity_id, field='username')
