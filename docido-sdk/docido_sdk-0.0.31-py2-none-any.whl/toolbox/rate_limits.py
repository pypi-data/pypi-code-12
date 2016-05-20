import functools
import random
import sys

from requests.exceptions import RequestException

from docido_sdk.toolbox.edsl import kwargsql
from docido_sdk.crawler import Retry

MAX_COLLISIONS = 5
DEFAULT_RETRY = 60


def truncated_exponential_backoff(slot_delay, collision=0, max_collisions=5):
    """Truncated Exponential Backoff
    see https://en.wikipedia.org/wiki/Exponential_backoff
    """
    if collision == max_collisions:
        collision = 0
    slots = random.randint(0, collision)
    return slots * slot_delay


def teb_retry(exc=RequestException,
              when=dict(response__status_code=429),
              delay='response__headers__Retry-After',
              max_collisions=MAX_COLLISIONS,
              default_retry=DEFAULT_RETRY):
    """Decorator catching rate limits exceed events during a crawl task.
    It retries the task later on, following a truncated exponential backoff.
    """
    def wrap(f):
        @functools.wraps(f)
        def wrapped_f(*args, **kwargs):
            attempt = kwargs.pop('teb_retry_attempt', 0)
            try:
                return f(*args, **kwargs)
            except exc as e:
                if kwargsql.and_(e, **when):
                    try:
                        retry_after = kwargsql.get(e, delay)
                    except:
                        retry_after = default_retry
                    else:
                        if retry_after is not None:
                            retry_after = int(retry_after)
                        else:
                            retry_after = default_retry
                    countdown = retry_after + truncated_exponential_backoff(
                        retry_after, attempt % max_collisions)
                    raise Retry(kwargs=dict(attempt=attempt + 1),
                                countdown=countdown)
                else:
                    raise e, None, sys.exc_info()[2] # flake8: noqa.
        return wrapped_f
    return wrap
