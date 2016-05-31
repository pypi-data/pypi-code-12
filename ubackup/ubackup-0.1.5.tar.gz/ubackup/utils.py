from __future__ import division

from ubackup import settings
from subprocess import Popen, PIPE
import math
import os
import imp
import re
import collections
import functools


class memoized(object):
    '''Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    '''
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        return functools.partial(self.__call__, obj)


def total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10 ** 6) / 10 ** 6


def filesizeformat(bytes, precision=2):
    """Returns a humanized string for a given amount of bytes"""
    bytes = int(bytes)
    if bytes is 0:
        return '0B'
    log = math.floor(math.log(bytes, 1024))
    return "%.*f%s" % (
        precision,
        bytes / math.pow(1024, log),
        ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
        [int(log)]
    )


def stream_shell(cmd, cwd=None, stdin=None):
    with open(os.devnull, 'w') as devnull:
        params = {
            'args': [cmd],
            'stdout': PIPE,
            'stderr': devnull,
            'shell': True,
            'bufsize': 1
        }

        if cwd is not None:
            params['cwd'] = cwd
        if stdin is not None:
            params['stdin'] = stdin

        process = Popen(**params)

    return process.stdout


def crypt_stream(stream, crypt_key):
    return stream_shell(
        cmd="openssl enc -aes-256-ecb -salt -pass pass:%s" % crypt_key,
        stdin=stream)


def decrypt_stream(stream, crypt_key):
    return stream_shell(
        cmd="openssl enc -aes-256-ecb -salt -d -pass pass:%s" % crypt_key,
        stdin=stream)


def gzip_stream(stream):
    return stream_shell(
        cmd='gzip -fc',
        stdin=stream)


def unzip_stream(stream):
    return stream_shell(
        cmd='gzip -dc',
        stdin=stream)


def md5_stream(stream):
    md5_hash = stream_shell(
        cmd='md5sum',
        stdin=stream).read()
    return re.findall(r'^(\w+)', md5_hash)[0]


def merge_settings(settings_path=None):
    import ubackup
    try:
        import ubackup.user_settings
    except ImportError:
        # Load user settings and override app settings
        if settings_path is None:
            settings_path = os.environ.get('SETTINGS_PATH', settings.DEFAULT_SETTINGS_PATH)

        if settings_path is not None and os.path.exists(settings_path):
            ubackup.user_settings = imp.load_source('ubackup.user_settings', settings_path)
            for key, value in ubackup.user_settings.__dict__.items():
                if not key.startswith('_'):
                    setattr(settings, key, value)
