# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from .processors import Match
from .processors import MatchError
from .processors import MethodProcessor
from .processors import PathProcessor
import logging
import operator

PROCESSORS = [
    PathProcessor('path'),
    MethodProcessor('method', optional=True),
]

logger = logging.getLogger('avenue')


class AvenueException(Exception):
    pass


class Skip(AvenueException):
    pass


class NotFound(AvenueException):
    pass


class Avenue(object):
    def __init__(self, processors=None):
        self.routes = list()
        self.processors = processors or PROCESSORS

    def attach(self, **kwargs):
        def inner(func):
            self.routes.append(Route(self, kwargs, func))
            return func

        return inner

    def match(self, **kwargs):
        values = [[p, kwargs.get(p.name)] for p in self.processors]
        matches = list()

        for route in self.routes:
            try:
                match = Match()
                for processor, value in values:
                    match.update(processor(value, route))
            except MatchError:
                pass
            else:
                matches.append([route, match])

        if len(matches):
            size = max(map(len, [m[1].score for m in matches]))
            matches = list(filter(lambda m: len(m[1].score) == size, matches))
            matches.sort(key=operator.itemgetter(1))

        logger.debug('Matched %s', [v[1] for v in values])
        for match in matches:
            logger.debug('%s', match)

        return matches

    def solve(self, **kwargs):
        wrap = kwargs.pop('wrap', None)

        for path, match in self.match(**kwargs):
            try:
                if callable(wrap):
                    callback = wrap(path.func)
                else:
                    callback = path.func

                return callback(**match.kwargs)
            except Skip:
                logger.debug('Callback raised Skip for match %s', match)

        raise NotFound()


class Route(object):
    def __init__(self, avenue, kwargs, func):
        self.avenue = avenue
        self.kwargs = kwargs
        self.func = func
