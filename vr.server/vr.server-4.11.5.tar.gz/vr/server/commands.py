import argparse
import os
import shlex

from six.moves import input

from django import setup
from django.core import management


def start_celery():
    setup()

    parser = argparse.ArgumentParser(description='Start the worker daemon')

    parser.add_argument('--queues', default=None,
                        help='limit this instance to the given queues')

    parser.add_argument('--exclude-queues', default=None,
                        help='queues to exclude in this instance')

    parser.add_argument('--loglevel', default='warning',
                        help='Specify celery loglevel')

    kwargs = dict()
    args = parser.parse_args()

    if args.queues is not None:
        kwargs['queues'] = args.queues
    elif 'VR_QUEUES' in os.environ:
        kwargs['queues'] = os.getenv('VR_QUEUES')

    if args.exclude_queues is not None:
        kwargs['exclude-queues'] = args.exclude_queues
    elif 'VR_EXCLUDE_QUEUES' in os.environ:
        kwargs['exclude-queues'] = os.getenv('VR_EXCLUDE_QUEUES')

    if args.loglevel is not None:
        kwargs['loglevel'] = args.loglevel

    management.call_command('celeryd', **kwargs)

def start_celerybeat():
    setup()
    management.call_command('celerybeat', pidfile=None)

def run_migrations():
    setup()
    args = shlex.split(os.getenv('MIGRATE_ARGS', ''))
    management.call_command('migrate', *args)

    if os.getenv('SLEEP_FOREVER') == 'true':
        input()
