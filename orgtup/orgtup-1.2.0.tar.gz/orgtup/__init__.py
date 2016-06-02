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

S3Path = namedtuple(
    'S3Path', (
        'bucket',
        'key',
    )
)

ElasticBeanstalkAppEnv = namedtuple(
    'ElasticBeanstalkAppEnv', (
        'application_name',
        'environment_name',
    )
)
