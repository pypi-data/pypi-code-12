"""
.. module: bobo.aws.sts
    :platform: Unix
    :copyright: (c) 2015 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
.. moduleauthor:: Patrick Kelley <patrick@netflix.com>
"""
from functools import wraps
import boto3
import dateutil.tz
import datetime

from botor.decorators import rate_limited
CACHE = {}


def _client(service, region, role):
    return boto3.client(
        service,
        region_name=region,
        aws_access_key_id=role['Credentials']['AccessKeyId'],
        aws_secret_access_key=role['Credentials']['SecretAccessKey'],
        aws_session_token=role['Credentials']['SessionToken']
    )


def _resource(service, region, role):
    return boto3.resource(
        service,
        region_name=region,
        aws_access_key_id=role['Credentials']['AccessKeyId'],
        aws_secret_access_key=role['Credentials']['SecretAccessKey'],
        aws_session_token=role['Credentials']['SessionToken']
    )


@rate_limited()
def sts_conn(service, service_type='client', future_expiration_minutes=15):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            should_assume = kwargs.pop("should_assume", True)

            if should_assume:
                key = (
                    kwargs.get('account_number'),
                    kwargs.get('assume_role'),
                    kwargs.get('session_name'),
                    kwargs.get('region', 'us-east-1'),
                    service_type,
                    service
                )

                if key in CACHE:
                    (val, exp) = CACHE[key]
                    now = datetime.datetime.now(dateutil.tz.tzutc()) \
                        + datetime.timedelta(minutes=future_expiration_minutes)
                    if exp > now:
                        kwargs[service_type] = val
                        kwargs.pop('account_number', None)
                        kwargs.pop('assume_role', None)
                        kwargs.pop('session_name', None)
                        kwargs.pop('region', None)
                        return f(*args, **kwargs)
                    else:
                        del CACHE[key]

                sts = boto3.client('sts')
                arn = 'arn:aws:iam::{0}:role/{1}'.format(
                    kwargs.pop('account_number'),
                    kwargs.pop('assume_role')
                )
                role = sts.assume_role(RoleArn=arn, RoleSessionName=kwargs.pop('session_name', 'botor'))

                if service_type == 'client':
                    kwargs[service_type] = _client(service, kwargs.pop('region', 'us-east-1'), role)
                elif service_type == 'resource':
                    kwargs[service_type] = _resource(service, kwargs.pop('region', 'us-east-1'), role)

                CACHE[key] = (kwargs[service_type], role['Credentials']['Expiration'])

            return f(*args, **kwargs)
        return decorated_function
    return decorator
