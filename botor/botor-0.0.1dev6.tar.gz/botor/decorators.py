"""
.. module: bobo.exceptions
    :platform: Unix
    :copyright: (c) 2015 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
.. moduleauthor:: Patrick Kelley <patrick@netflix.com>
.. moduleauthor:: Mike Grima <mgrima@netflix.com>
"""
import functools
import botocore
import time
import boto

RATE_LIMITING_ERRORS = ['Throttling', 'RequestLimitExceeded']


def rate_limited(max_attempts=None, max_delay=4):
    def decorator(f):
        metadata = {
            'count': 0,
            'delay': 0
        }

        @functools.wraps(f)
        def decorated_function(*args, **kwargs):

            def increase_delay(e):
                if metadata['delay'] == 0:
                    metadata['delay'] = 1
                elif metadata['delay'] < max_delay:
                    metadata['delay'] *= 2

                if max_attempts and metadata['count'] > max_attempts:
                    raise e

            metadata['count'] = 0
            while True:
                metadata['count'] += 1
                if metadata['delay'] > 0:
                    time.sleep(metadata['delay'])
                try:
                    retval = f(*args, **kwargs)
                    metadata['delay'] = 0
                    return retval
                except botocore.exceptions.ClientError as e:
                    if e.response["Error"]["Code"] not in RATE_LIMITING_ERRORS:
                        raise e
                    increase_delay(e)
                except boto.exception.BotoServerError as e:
                    if e.error_code not in RATE_LIMITING_ERRORS:
                        raise e
                    increase_delay(e)

        return decorated_function

    return decorator
