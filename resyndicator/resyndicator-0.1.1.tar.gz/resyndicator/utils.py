import uuid
import hashlib
import signal
import IPython
from collections import OrderedDict
from itertools import groupby
from . import settings


def ipython(args):
    IPython.embed()


def urn_from_string(string):
    # MD5 just because the length fits (16 bytes)
    digest = hashlib.md5(string.encode('utf-8')).digest()
    return str(uuid.UUID(bytes=digest).urn)


def typed_text(text, type):
    if text:
        return {'text': text, 'type': type}


def itertimeout(iterable, timeout):
    class TimeoutException(Exception):
        pass
    def raise_timeout(*args, **kwargs):
        raise TimeoutException(
            'Timeout ({timeout} s)'.format(timeout=timeout))
    signal.signal(signal.SIGALRM, raise_timeout)
    for item in iterable:
        signal.alarm(timeout)
        yield item
    signal.alarm(0)


def lgroupby(*args, **kwargs):
    return ((key, list(value)) for key, value in groupby(*args, **kwargs))


class Insert:

    def __init__(self, major, minor, start=None, stop=None):
        self.major = major
        self.minor = minor
        if start and stop:
            return self[start:stop]

    def __getitem__(self, slice_):
        start = slice_.start
        stop = slice_.stop
        return self.major[:start] + self.minor + self.major[stop:]


def sub_slices(string, repls):
    parts = []
    last_stop = 0
    for (start, stop), repl in sorted(repls.items()):
        assert start >= last_stop, 'Intervals must not overlap'
        parts.append(string[last_stop:start])
        parts.append(repl)
        last_stop = stop
    parts.append(string[last_stop:])
    return ''.join(parts)


class FeedTemplate:

    @staticmethod
    def feed():
        return {
            'feed': OrderedDict([
                ('@xmlns', 'http://www.w3.org/2005/Atom'),
                ('id', None),
                ('title', None),
                ('author', {
                    'name': 'Resyndicator'
                }),
                ('updated', None),  # e.g., '2016-05-20T09,57,34Z'
                ('link', [
                    {
                        '@href': None,
                        '@rel': 'self'
                    },
                    {
                        '@href': settings.HUB,
                        '@rel': 'hub'
                    }
                ]),
                ('generator', 'Resyndicator'),
                ('entry', []),
            ])
        }

    @staticmethod
    def entry():
        return {
            'id': None,
            'updated': None,  # e.g., '2016-05-20T09:57:34Z'
            'published': None,  # e.g., '2016-05-20T09:57:34Z'
            'title': None,
            'author': {
                'name': None,
            },
            'link': {
                '@href': None,
                '@rel': 'alternate'
            },
            'summary': {
                '@type': None,  # html or text
                '#text': None,
            },
            'content': {
                '@type': None,  # html or text
                '#text': None,
            },
            'source': {
                'id': None,
                'link': {
                    '@href': None,
                    '@rel': 'self',
                },
                'title': None,
            },
        }
