# -*- coding: utf-8 -*-
import abc
import collections
import re
from watson.http import REQUEST_METHODS, MIME_TYPES
from watson.common.imports import get_qualified_name

__all__ = ('Base', 'Literal', 'Segment', 'RouteMatch')

# route: The matched route
# params: The parameters that have been matched
RouteMatch = collections.namedtuple('RouteMatch', 'route params')


class Base(metaclass=abc.ABCMeta):
    """Matches a request to a specific pattern.

    The only required attribute of a route is the 'path' key. This defines the
    URL path that it must be matched against.

    Additional options can be added to 'requires' to force additional matching.

    - subdomain: The subdomain to match
    - format: The accept format (/path.xml or Accept: text/xml in headers)

    Child routes can also be added, to less the amount of typing required to
    define further routes.

    Attributes:
        name (string): The name of the route, referenced by the the Router.
        path (string): The url path that should be matched.
        accepts (tuple): The REQUEST_METHODS that are accepted.
        requires (dict): A dict of values that must be matched, can be a regular expression.
        priority (int): If multiple matching routes are found, determine relevance.

    Example:

    .. code-block: python

        routes = {
            'home': {
                'path': '/',
                'accepts': ('GET',),
                'options': {}
                'defaults': {},
                'requires': {
                    'format': 'xml'
                },
                'children': {
                    'about': {
                        'path': 'about'
                    }
                }
            }
        }

        router = Router(routes=routes)
        matches = [match for match in router.matches(Request(environ))]
    """
    __slots__ = ('_name', '_path', '_accepts', '_requires', '_defaults',
                 '_options', '_priority', '_regex_requires')

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def accepts(self):
        return self._accepts

    @property
    def requires(self):
        return self._requires

    @property
    def defaults(self):
        return self._defaults

    @property
    def options(self):
        return self._options

    @property
    def priority(self):
        return int(self._priority) or 1

    def __init__(self, name, path,
                 accepts=None, requires=None, defaults=None, options=None,
                 priority=1, **kwargs):
        self._name = name
        self._path = path
        self._accepts = accepts or REQUEST_METHODS
        self._requires = requires or {}
        self._defaults = defaults or {}
        self._options = options or {}
        self._priority = priority
        self._process_requires()

    def builder(cls, **definition):
        raise NotImplementedError()

    def _process_requires(self):
        self._regex_requires = {k: re.compile(v) for k, v in self.requires.items() if isinstance(v, str)}

    def assemble(self, prefix=None, **kwargs):
        raise NotImplementedError()

    def match(self, request):
        """Match the route to a request and return the matched parameters.

        Processes the route against the following requirements:

        - REQUEST_METHOD
        - Subdomain
        - Format
        - GET vars

        If any of the above requirements fail, no parameters are returned, and
        the route is considered invalid.

        Methods that override this should return a RouteMatch(self, params)
        object.

        Args:
            request (watson.http.messages.Request): The request to match.
        """
        params = self.defaults.copy()
        requires = self.requires.copy()
        if not request.method in self._accepts:
            return None
        if 'subdomain' in self.requires:
            del requires['subdomain']
            subdomain = self.requires['subdomain']
            if isinstance(subdomain, (list, tuple)):
                if request.url.subdomain not in subdomain:
                    return None
            elif request.url.subdomain != subdomain:
                return None
        if 'format' in self.requires:
            del requires['format']
            accept_headers = request.environ.get('HTTP_ACCEPT')
            formats = [format for format
                       in MIME_TYPES if accept_headers in MIME_TYPES[format]]
            if formats:
                for format in formats:
                    if self._regex_requires['format'].match(format):
                        params['format'] = format
            else:
                return None
        if request.method == 'GET' and requires and request.get:
            for key, value in request.get.items():
                regex = self._regex_requires.get(key, None)
                if regex:
                    if regex.match(value):
                        params[key] = value
                    else:
                        return None
        return params

    def __repr__(self):
        return (
            '<{0} name:{1} path:{2}>'.format(
                get_qualified_name(self),
                self.name,
                self.path)
        )

segments_pattern = re.compile('(?P<static>[^:\[\]]*)(?P<token>[:\[\]]|$)')
token_pattern = re.compile('(?P<name>[^:/\[\]]+)')
optional_segment_string = '(?:{value})?'
value_pattern_string = '(?P<{value}>{end})'
end_pattern_string = '[^/]+'


def segments_from_path(path):
    """Converts a segmented path into a regular expression.

    A segmented route can be any of the following:

    - /route/:segment, segment will be a required parameter
    - /route[/:segment], segment will be an optional parameter
    - /route[/:segment[/:nested]] - segment will be a optional parameter

    Inspired by both Rails and ZF2.

    Args:
        path: the segmented path to convert to regex

    Returns:
        list: A list of segments based on the path.
    """
    depth, segments = 0, []
    depth_segments = [segments]
    while path:
        matches = segments_pattern.search(path)
        segment_matches = matches.groups()
        offset = '{0}{1}'.format(segment_matches[0], segment_matches[1])
        path = path[len(offset):]
        token = matches.group('token')
        static = matches.group('static')
        if static:
            depth_segments[depth].append(('static', static))
        if token == ':':
            named_segment = token_pattern.search(path)
            segment = named_segment.groupdict()['name']
            depth_segments[depth].append(('segment', segment))
            path = path[len(segment):]
        elif token == '[':
            depth += 1
            current_depth = depth - 1
            total_depths = len(depth_segments)
            if total_depths <= depth:
                depth_segments.append([])
            depth_segments[current_depth].append(('optional', []))
            depth_segments[depth] = depth_segments[current_depth][len(depth_segments[current_depth]) - 1][1]
        elif token == ']':
            del depth_segments[depth]
            depth -= 1
            if depth < 0:
                raise ValueError('Bracket mismatch detected.')
        else:
            break
    del depth_segments
    return segments


def regex_from_segments(segments, requires=None):
    """Converts a list of segment tuple pairs into a regular expression string.

    Args:
        segments (list): The segment tuple pairs to convert.
        requires (dict): Key/value pairs to be used in each segment.

    Returns:
        string: The regex for the segments
    """
    regex = []
    for type_, value in segments:
        if type_ == 'static':
            regex.append(re.escape(value))
        elif type_ == 'optional':
            regex.append(
                optional_segment_string.format(
                    value=regex_from_segments(value, requires)))
        else:
            regex.append(
                value_pattern_string.format(
                    value=value,
                    end=requires.get(value, end_pattern_string)))
    regex.append('$')
    return ''.join(regex)


def path_from_segments(segments, params, optional=False):
    """Converts a list of segment tuple pairs into a url path.

    Args:
        segments (list): The segment tuple pairs to convert.
        params (dict): Key/value pairs for each segment and its value.
    """
    path = []
    for segment in segments:
        type_, name = segment
        optional = optional if optional else type_ == 'optional'
        if isinstance(name, list):
            path.append(path_from_segments(name, params, optional))
        else:
            if type_ == 'segment':
                if name in params and params[name]:
                    path.append(str(params[name]))
                elif optional:
                    remove_segments = len(segments) - 1
                    path = path[0:-remove_segments]
                else:
                    raise KeyError("Missing '{0}' in params.".format(name))
            else:
                path.append(name)
    return ''.join(path)


class Segment(Base):
    """Matches a request against a regular expression.

    Attributes:
        regex (SRE_Pattern): The regex pattern used to match the path.
        segments (list): A tuple pair list of segments for the route.
    """

    __slots__ = ('_regex', '_segments')

    @property
    def regex(self):
        return self._regex

    @regex.setter
    def regex(self, regex):
        if isinstance(regex, str):
            self._segments = segments_from_path(regex)
            regex_string = regex_from_segments(self.segments, self.requires)
            regex = re.compile(regex_string)
        self._regex = regex

    @property
    def segments(self):
        return self._segments

    def __init__(self, name, path=None,
                 accepts=None, requires=None, defaults=None, options=None,
                 priority=1, regex=None, **kwargs):
        if not path and not regex:
            raise TypeError(
                'You must specify either path or regex for the route named {0}'.format(name))
        super(Segment, self).__init__(
            name, path,
            accepts, requires, defaults, options, priority, **kwargs)
        self.regex = regex if regex else path

    def assemble(self, prefix=None, **kwargs):
        """Converts the route into a path.

        Applies any keyword arguments as params on the route.

        Example:

        .. code-block:: python

            route = Route('search', path='/search/:keyword')
            route.assemble(keyword='test')  # /search/test
        """
        params = collections.ChainMap(kwargs or {}, self.defaults)
        path = path_from_segments(self.segments, params)
        return prefix + path if prefix else path

    def match(self, request):
        params = super(Segment, self).match(request)
        if params is None:
            return None
        matches = self.regex.match(request.environ.get('PATH_INFO'))
        if matches:
            params = dict(params, **matches.groupdict())
            for k, v in self.defaults.items():
                if params[k] is None:
                    params[k] = v
            return RouteMatch(self, params)
        return None

    @classmethod
    def builder(cls, **definition):
        if ('regex' in definition
                or ('path' in definition
                    and any((c in {'[', ':'}) for c in definition['path']))):
            return cls(**definition)
        raise TypeError('Not a valid Segment')

    def __repr__(self):
        class_ = get_qualified_name(self)
        if self.path:
            return (
                '<{0} name:{1} path:{2} match:{3}>'.format(
                    class_,
                    self.name,
                    self.path,
                    self.regex.pattern)
            )
        return (
            '<{0} name:{1} match:{2}>'.format(
                class_,
                self.name,
                self.regex.pattern)
        )


class Literal(Base):
    """Matches a request against a literal path.

    A literal path is classified as /example/path where there are no dynamic
    elements.
    """

    def assemble(self, prefix=None, **kwargs):
        """Converts the route into a path.

        Applies any keyword arguments as params on the route.

        Example:

        .. code-block:: python

            route = Literal('search', path='/search/:keyword')
            route.assemble(keyword='test')  # /search/test
        """
        return prefix + self.path if prefix else self.path

    def match(self, request):
        params = super(Literal, self).match(request)
        if params is not None and request.environ['PATH_INFO'] == self.path:
            return RouteMatch(self, params=params)
        return None

    @classmethod
    def builder(cls, **definition):
        return cls(**definition)

# Deprecated, will be removed in the next major version

BaseRoute = Base
LiteralRoute = Literal
SegmentRoute = Segment
