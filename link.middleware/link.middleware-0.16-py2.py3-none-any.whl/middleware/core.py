# -*- coding: utf-8 -*-

from b3j0f.utils.iterable import isiterable

from six.moves.urllib.parse import urlunsplit, SplitResult
from six.moves.urllib.parse import urlsplit, parse_qs
from six.moves.urllib.parse import urlencode

from six import add_metaclass, string_types

from inspect import getmembers, isroutine


MIDDLEWARES_BY_PROTOCOLS = {}
MIDDLEWARES_BY_URL = {}


class MetaMiddleware(type):
    """
    Metaclas registering middlewares.
    """

    def __init__(cls, name, bases, attrs):
        super(MetaMiddleware, cls).__init__(name, bases, attrs)

        for protocol in cls.protocols():
            middlewares = MIDDLEWARES_BY_PROTOCOLS.setdefault(protocol, [])
            middlewares.append(cls)


@add_metaclass(MetaMiddleware)
class Middleware(object):
    """
    Basic middleware class, resolvable via URLs.
    """

    __constraints__ = []
    __protocols__ = []
    __features__ = []

    class Error(Exception):
        pass

    @classmethod
    def protocols(cls):
        """
        Get all protocols supported by class.

        :returns: list of protocols
        :rtype: list
        """

        bases = cls.mro()

        if hasattr(cls, '__protocols__'):
            result = cls.__protocols__

        else:
            result = []

        for base in bases:
            if hasattr(base, '__protocols__'):
                result = base.__protocols__ + result

        return result

    @classmethod
    def constraints(cls):
        """
        Get all constraints enforced by class.
        A constraint is used when the middleware is instantiated with a child
        middleware (``protocol1+protocol2://``). The child middleware must be
        a subclass of each class specified by the constraint.

        :returns: list of constraints
        :rtype: list
        """

        bases = cls.mro()
        result = []

        for base in reversed(bases):
            if hasattr(base, '__constraints__'):
                result += base.__constraints__

        if hasattr(cls, '__constraints__'):
            result += cls.__constraints__

        return result

    @staticmethod
    def get_middlewares_by_protocols(protocols):
        """
        Get list of middlewares implementing every listed protocol.

        :param protocols: list of protocols
        :type protocols: str or list

        :returns: list of middleware
        :rtype: list
        """

        if not isiterable(protocols, exclude=string_types):
            protocols = [protocols]

        middlewares = [
            set(MIDDLEWARES_BY_PROTOCOLS.get(protocol, []))
            for protocol in protocols
        ]

        return list(set.intersection(*middlewares))

    @staticmethod
    def get_middleware_by_uri(uri, cache=True):
        """
        Resolve URI to instantiate a middleware.

        :param uri: URI pointing to middleware
        :type uri: str
        :param cache: Cache the instantiated middleware (default: True)
        :type cache: bool
        :returns: Pointed middleware
        :rtype: Middleware
        """

        middleware = None

        if uri not in MIDDLEWARES_BY_URL:
            parseduri = urlsplit(uri)

            protocols = reversed(parseduri.scheme.split('+'))
            path = parseduri.path
            query = parse_qs(parseduri.query)

            for key in query.keys():
                if key.endswith('[]'):
                    query[key[:-2]] = query.pop(key)

                else:
                    query[key] = query[key][0]

            if path:
                path = path[1:].split('/')

            for protocol in protocols:
                cls = None

                classes = Middleware.get_middlewares_by_protocols(protocol)

                if len(classes) == 0:
                    raise Middleware.Error(
                        'Unknown protocol: {0}'.format(protocol)
                    )

                if middleware is not None:
                    for candidate in classes:
                        bases = candidate.constraints()

                        for base in bases:
                            if base in middleware.__class__.mro():
                                cls = candidate
                                break

                        if cls is not None:
                            break

                    else:
                        raise Middleware.Error(
                            'No middleware <{0}> found for: {1}'.format(
                                protocol,
                                middleware.__class__.__name__
                            )
                        )

                else:
                    cls = classes[0]

                netloc = parseduri.netloc.split('@', 1)

                if len(netloc) == 2:
                    authority, hosts = netloc
                    authority = authority.split(':', 1)

                    if len(authority) == 2:
                        username, password = authority

                    else:
                        username = authority
                        password = None

                    hosts = hosts.split(',')

                else:
                    username, password = None, None
                    hosts = netloc[0].split(',')

                parsedhosts = []

                for host in hosts:
                    host = host.split(':', 1)

                    if len(host) == 2:
                        host, port = host
                        port = int(port)

                    else:
                        host = host
                        port = None

                    parsedhosts.append((host, port))

                kwargs = {
                    'user': username,
                    'pwd': password,
                    'hosts': parsedhosts,
                    'path': path,
                    'fragment': parseduri.fragment
                }
                kwargs.update(query)

                child = middleware if middleware is not None else None
                middleware = cls(**kwargs)
                middleware.set_child_middleware(child)

            if cache:
                MIDDLEWARES_BY_URL[uri] = middleware

        else:
            middleware = MIDDLEWARES_BY_URL[uri]

        return middleware

    def __init__(
        self,
        user=None,
        pwd=None,
        hosts=None,
        path=None,
        fragment='',
        **kwargs
    ):
        super(Middleware, self).__init__()

        if hosts is None:
            hosts = []

        self.user = user
        self.pwd = pwd
        self.hosts = hosts
        self.path = path
        self.fragment = fragment

        self._child = None

    def tourl(self):
        """
        Get URL from current middleware.

        :returns: URL pointing to this middleware.
        :rtype: str
        """

        if self in MIDDLEWARES_BY_URL.values():
            for uri, middleware in MIDDLEWARES_BY_URL.items():
                if middleware is self:
                    return uri

        else:
            kwargs = {
                name: var
                for name, var in getmembers(self, lambda m: not isroutine(m))
                if name[0] != '_' and name not in [
                    'user', 'pwd', 'hosts', 'path', 'fragment'
                ]
            }

            path = self.path

            if path:
                path = '/'.join([''] + path)

            query = urlencode(kwargs)

            # build netloc

            if self.user:
                if self.pwd:
                    authority = '{0}:{1}@'.format(self.user, self.pwd)

                else:
                    authority = '{0}@'.format(self.user)

            else:
                authority = ''

            hosts = []

            for host, port in self.hosts:
                if port is not None:
                    hosts.append('{0}:{1}'.format(host, port))

                else:
                    hosts.append(host)

            hosts = ','.join(hosts)

            netloc = '{0}{1}'.format(authority, hosts)

            return urlunsplit(
                SplitResult(
                    scheme=self.__class__.protocols()[-1],
                    netloc=netloc,
                    path=path,
                    fragment=self.fragment,
                    query=query
                )
            )

    def set_child_middleware(self, middleware):
        """
        Set child middleware (make sure the child middleware validates the
        middleware constraints).

        :param middleware: Child middleware
        :type middleware: Middleware
        """

        bases = self.__class__.constraints()

        for base in bases:
            if base in middleware.__class__.mro():
                break

        else:
            raise Middleware.Error(
                'Middleware <{0}> does not validates <{1}> constraints'.format(
                    middleware.__class__.__name__,
                    self.__class__.__name__
                )
            )

        self._child = middleware

    def get_child_middleware(self):
        """
        Get child middleware.

        :returns: Child middleware or None
        :rtype: Middleware
        """

        return self._child

    def features(self):
        """
        Get all features supported by middleware (and children).

        :returns: list of features by middleware
        :rtype: list of tuple (middleware, feature)
        """

        bases = self.__class__.mro()
        result = []

        for base in reversed(bases):
            if hasattr(base, '__features__'):
                result += [
                    (self, feature_cls)
                    for feature_cls in base.__features__
                ]

        if hasattr(self.__class__, '__features__'):
            result += [
                (self, feature_cls)
                for feature_cls in self.__class__.__features__
            ]

        child = self.get_child_middleware()

        if child is not None:
            result += child.features()

        return result

    def has_feature(self, name):
        """
        Check if feature exists.

        :param name: feature's name
        :type name: str

        :returns: ``True`` if feature exists, ``False`` otherwise
        :rtype: bool
        """

        for _, feature in self.features():
            if feature.name == name:
                return True

        return False

    def get_feature(self, name, *args, **kwargs):
        """
        Instantiate feature.

        :param name: feature's name
        :type name: str

        :param args: Positional arguments for feature's constructor
        :param kwargs: Keyword arguments for feature's constructor

        :returns: Newly created feature
        :rtype: Feature

        :raises AttributeError: When feature does not exist
        """

        for middleware, feature in self.features():
            if feature.name == name:
                return feature(middleware, *args, **kwargs)

        raise AttributeError('No such feature: {0}'.format(name))


class Feature(object):
    """
    Base class for middleware's feature.

    :param middleware: Middleware providing this feature
    :type middleware: Middleware
    """

    name = None

    def __init__(self, middleware, *args, **kwargs):
        super(Feature, self).__init__(*args, **kwargs)

        self.middleware = middleware
