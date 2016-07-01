from __future__ import absolute_import, division, print_function

from pandora import CONVERTERS
from pandora import Path


class Match(object):
    def __init__(self, score=None, kwargs=None):
        self.score = score or list()
        self.kwargs = kwargs or dict()

    def update(self, result):
        if type(result) is int:
            self.score.append(result)
        elif isinstance(result, Match):
            self.score.append(result.score)
            self.kwargs.update(result.kwargs)

    def __lt__(self, other):
        return any([s < other.score[sx] for sx, s in enumerate(self.score)])

    def __repr__(self):
        return '<Match (score={:s})>'.format(repr(self.score))


class MatchError(Exception):
    pass


class Processor(object):
    def __init__(self, name, optional=False):
        self.name = name
        self.optional = optional

    def prepare(self, value, route):
        argument = route.kwargs.get(self.name)

        if not argument and not self.optional:
            message = 'Cannot run route, `{:s}` is not optional.'.format(
                self.name)

            raise RuntimeError(message)

        if argument and value is None:
            message = 'Value not found, `{:s}` is not optional.'.format(
                self.name)

            raise MatchError(message)

        return argument, value


class PathProcessor(Processor):
    def __init__(self, name, optional=False, converters=None):
        super(PathProcessor, self).__init__(name, optional)
        self.cache = dict()
        self.converters = converters or CONVERTERS

    def __call__(self, value, route):
        """

        :type value: mixed
        :type route: avenue.Route
        :rtype: Match
        """
        argument, value = self.prepare(value, route)

        if not argument:
            return True, -100, 100

        if argument not in self.cache:
            self.cache[argument] = Path(argument, self.converters,
                                        split='/')

        path = self.cache[argument]
        match = path(value)

        if match is not None:
            return Match(path, match)

        raise MatchError('Path does not match, `{:s}` != `{:s}`'.format(
            path.original, argument))


class MethodProcessor(Processor):
    def __call__(self, value, route):
        """

        :type value: mixed
        :type route: avenue.Route
        :rtype: Match
        """
        argument, value = self.prepare(value, route)

        if not argument:
            return 0
        elif value == argument:
            return -1
        else:
            error = 'Method does not match, `{:s}` != `{:s}`'.format(
                value, argument)
            raise MatchError(error)
