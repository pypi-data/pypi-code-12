# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
"""
riko.modules.pipestrfind
~~~~~~~~~~~~~~~~~~~~~~~~
Provides functions for searching for a portion of a string.

You end a `start` and/or `end` string to search for, and a string to search.
If your input string is "ABCDEFG", then a `start` string of `B` gives you a
resulting string of "CDEFG". You can optionally search with regex patterns as
well.

Examples:
    basic usage::

        >>> from riko.modules.pipestrfind import pipe
        >>> conf = {'start': 'hel'}
        >>> next(pipe({'content': 'hello world'}, conf=conf))['strfind']
        u'lo world'

Attributes:
    OPTS (dict): The default pipe options
    DEFAULTS (dict): The default parser options
"""
from __future__ import (
    absolute_import, division, print_function, unicode_literals)

import re

from builtins import *

from . import processor
from riko.lib.log import Logger

OPTS = {'ftype': 'text', 'ptype': 'text', 'field': 'content'}
DEFAULTS = {'regex': False}
logger = Logger(__name__).logger


def parser(word, objconf, skip, **kwargs):
    """ Parses the pipe content

    Args:
        word (str): The string to parse
        objconf (obj): The pipe configuration (an Objectify instance)
        skip (bool): Don't parse the content
        kwargs (dict): Keyword arguments

    Kwargs:
        assign (str): Attribute to assign parsed content (default: strfind)
        feed (dict): The original item

    Returns:
        Tuple(dict, bool): Tuple of (item, skip)

    Examples:
        >>> from riko.lib.utils import Objectify
        >>>
        >>> item = {'content': 'hello world'}
        >>> conf = {'start': 'hel'}
        >>> kwargs = {'feed': item, 'conf': conf}
        >>> parser(item['content'], Objectify(conf), False, **kwargs)[0]
        u'lo world'
    """
    if skip:
        value = kwargs['feed']
    elif objconf.regex:
        s = re.split(objconf.start, word)[1] if objconf.start else word
        value = re.split(objconf.end, s)[0] if objconf.end else s
    else:
        s = word.split(objconf.start)[1] if objconf.start else word
        value = s.split(objconf.end)[0] if objconf.end else s

    return value.strip(), skip


@processor(DEFAULTS, async=True, **OPTS)
def asyncPipe(*args, **kwargs):
    """A processor module that asynchronously finds a portion of a field string
    in a feed item.

    Args:
        item (dict): The entry to process
        kwargs (dict): The keyword arguments passed to the wrapper

    Kwargs:
        conf (dict): The pipe configuration. May contain the keys 'start',
            'end', or 'regex'.

            start (text): starting string (returns everything after this)
            end (text): ending string (returns everything before this)
            regex (bool): interpret `start` and `end` as regex patterns (
                default: False)

        assign (str): Attribute to assign parsed content (default: strfind)
        field (str): Item attribute from which to obtain the first number to
            operate on (default: 'content')

    Returns:
        Deferred: twisted.internet.defer.Deferred item with the found string

    Examples:
        >>> from twisted.internet.task import react
        >>> from riko.twisted import utils as tu
        >>>
        >>> def run(reactor):
        ...     callback = lambda x: print(next(x)['strfind'])
        ...     conf = {'start': 'hel'}
        ...     d = asyncPipe({'content': 'hello world'}, conf=conf)
        ...     return d.addCallbacks(callback, logger.error)
        >>>
        >>> try:
        ...     react(run, _reactor=tu.FakeReactor())
        ... except SystemExit:
        ...     pass
        ...
        lo world
    """
    return parser(*args, **kwargs)


@processor(**OPTS)
def pipe(*args, **kwargs):
    """A processor that finds a portion of a field string in a feed item.

    Args:
        item (dict): The entry to process
        kwargs (dict): The keyword arguments passed to the wrapper

    Kwargs:
        conf (dict): The pipe configuration. May contain the keys 'start',
            'end', or 'regex'.

            start (text): starting string (returns everything after this)
            end (text): ending string (returns everything before this)
            regex (bool): interpret `start` and `end` as regex patterns (
                default: False)

        assign (str): Attribute to assign parsed content (default: strfind)
        field (str): Item attribute from which to obtain the first number to
            operate on (default: 'content')

    Yields:
        dict: an item with the found string

    Examples:
        >>> conf = {'start': 'hel'}
        >>> next(pipe({'content': 'hello world'}, conf=conf))['strfind']
        u'lo world'
        >>> conf = {'start': 'r.*t', 'regex': 'true'}
        >>> next(pipe({'content': 'Greetings'}, conf=conf))['strfind']
        u'ings'
        >>> conf = {'start': 'r', 'end': 'gs'}
        >>> kwargs = {'conf': conf, 'field': 'title', 'assign': 'result'}
        >>> next(pipe({'title': 'Greetings'}, **kwargs))['result']
        u'eetin'
    """
    return parser(*args, **kwargs)
