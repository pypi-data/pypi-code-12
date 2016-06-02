"""Named tuples related to common services."""

from collections import namedtuple

GithubPersonalAccessToken = namedtuple(
    'GithubPersonalAccessToken', (
        'username',
        'key',
    )
)

AwsCredentials = namedtuple(
    'AwsCredentials', (
        'access_key_id',
        'secret_access_key',
    )
)
