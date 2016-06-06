# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
"""
riko.modules.pipeslugify
~~~~~~~~~~~~~~~~~~~~~~~~
Provides functions for slugifying text.

Examples:
    basic usage::

        >>> from riko.modules.pipeslugify import pipe
        >>> next(pipe({'content': 'Hello World'}))['slugify']
        'hello-world'

Attributes:
    OPTS (dict): The default pipe options
    DEFAULTS (dict): The default parser options
"""
from __future__ import (
    absolute_import, division, print_function, unicode_literals)

from builtins import *
from slugify import slugify

from . import processor
from riko.lib.log import Logger

OPTS = {'ftype': 'text', 'ptype': 'none', 'field': 'content'}
DEFAULTS = {}
logger = Logger(__name__).logger


def parser(word, _, skip, **kwargs):
    """ Parsers the pipe content

    Args:
        item (obj): The entry to process (a DotDict instance)
        _ (None): Ignored.
        skip (bool): Don't parse the content
        kwargs (dict): Keyword arguments

    Kwargs:
        assign (str): Attribute to assign parsed content (default: exchangerate)
        feed (dict): The original item

    Returns:
        Tuple(dict, bool): Tuple of (item, skip)

    Examples:
        >>> from riko.lib.utils import Objectify
        >>>
        >>> item = {'content': 'Hello World'}
        >>> kwargs = {'feed': item}
        >>> parser(item['content'], None, False, **kwargs)[0]
        'hello-world'
    """
    parsed = kwargs['feed'] if skip else slugify(word.strip())
    return parsed, skip


@processor(DEFAULTS, async=True, **OPTS)
def asyncPipe(*args, **kwargs):
    """A processor module that asynchronously slugifies the field of a feed item.

    Args:
        item (dict): The entry to process
        kwargs (dict): The keyword arguments passed to the wrapper

    Kwargs:
        assign (str): Attribute to assign parsed content (default: simplemath)
        field (str): Item attribute from which to obtain the first number to
            operate on (default: 'content')

    Returns:
        Deferred: twisted.internet.defer.Deferred item with concatenated content

    Examples:
        >>> from twisted.internet.task import react
        >>> from riko.twisted import utils as tu
        >>>
        >>> def run(reactor):
        ...     callback = lambda x: print(next(x)['slugify'])
        ...     d = asyncPipe({'content': 'Hello World'})
        ...     return d.addCallbacks(callback, logger.error)
        >>>
        >>> try:
        ...     react(run, _reactor=tu.FakeReactor())
        ... except SystemExit:
        ...     pass
        ...
        hello-world
    """
    return parser(*args, **kwargs)


@processor(**OPTS)
def pipe(*args, **kwargs):
    """A processor that slugifies the field of a feed item.

    Args:
        item (dict): The entry to process
        kwargs (dict): The keyword arguments passed to the wrapper

    Kwargs:
        assign (str): Attribute to assign parsed content (default: slugify)
        field (str): Item attribute from which to obtain the text to slugify
            (default: 'content')

    Yields:
        dict: an item with slugified content

    Examples:
        >>> next(pipe({'content': 'Hello World'}))['slugify']
        'hello-world'
    """
    return parser(*args, **kwargs)
