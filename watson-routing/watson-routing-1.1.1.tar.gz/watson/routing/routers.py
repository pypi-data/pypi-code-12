# -*- coding: utf-8 -*-
import abc
import collections
from watson.routing.routes import BaseRoute, LiteralRoute, SegmentRoute
from watson.common.contextmanagers import suppress
from watson.common.datastructures import dict_deep_update
from watson.common.imports import get_qualified_name


class Base(metaclass=abc.ABCMeta):

    """Responsible for maintaining a list of routes.

    Attributes:
        routes (OrderedDict): A dict of routes
    """
    _requires_sort = False
    _build_strategies = None
    _routes = None

    @property
    def routes(self):
        return self._routes

    def __init__(self, routes=None, build_strategies=None):
        default_build_strategies = (SegmentRoute.builder, LiteralRoute.builder)
        if not build_strategies:
            build_strategies = []
        build_strategies.extend(default_build_strategies)
        self._build_strategies = build_strategies
        self._routes = collections.OrderedDict()

    def build_route(self, **definition):
        """Converts a route definition into a specific route.
        """
        for strategy in self._build_strategies:
            with suppress(TypeError):
                return strategy(**definition)
        raise Exception(
            'No strategy is capable of building route {0}'.format(definition))

    def matches(self, request):
        """Match a request against all the routes.

        Args:
            request (watson.http.messages.Request): The request to match.

        Returns:
            A list of RouteMatch namedtuples.
        """
        self.sort()
        for name, route in self:
            route_match = route.match(request)
            if route_match:
                yield route_match

    def match(self, request):
        """Match a request against all the routes and return the first match.

        Args:
            request (watson.http.messages.Request): The request to match.

        Returns:
            The RouteMatch of the route.
        """
        for route_match in self.matches(request):
            return route_match
        return None

    def assemble(self, route_name, **kwargs):
        """Converts the route into a path.

        Applies any keyword arguments as params on the route. This is a
        convenience method for accessing the assemble method on an individual
        route.

        Args:
            route_name (string): The name of the route

        Raises:
            KeyError if the route does not exist on the router.
        """
        if route_name in self:
            return self.routes[route_name].assemble(**kwargs)
        else:
            raise KeyError(
                'No route named {0} can be found.'.format(route_name))

    def add_definition(self, definition):
        """Converts a route definition into a route.

        Args:
            definition (dict): The definition to add.
        """
        route = self.build_route(**definition)
        self._create_child_routes(definition, route)
        self.add_route(route)
        return route

    def add_route(self, route):
        """Adds an instantiated route to the router.

        Args:
            route (watson.routing.routes.BaseRoute): The route to add.
        """
        self._requires_sort = True
        self.routes[route.name] = route

    def sort(self):
        if self._requires_sort:
            self._routes = collections.OrderedDict(
                reversed(sorted(self.routes.items(),
                         key=lambda r: (r[1].priority, r[1].path))))
            self._requires_sort = False

    # Internals

    def __contains__(self, route_name):
        return route_name in self.routes

    def _create_child_routes(self, definition, parent_route):
        children = definition.get('children', ())
        for child in children:
            if isinstance(child, str):
                name, child = child, children[child]
            else:
                name = child['name']
            child['requires'] = dict_deep_update(child.get('requires', {}), parent_route.requires)
            child['defaults'] = dict_deep_update(child.get('defaults', {}), parent_route.requires)
            name = '{0}/{1}'.format(parent_route.name, name)
            if 'path' not in child:
                child['path'] = '/{}'.format(name)
            child['path'] = '{0}{1}'.format(parent_route.path, child['path'])
            child['name'] = name
            self.add_definition(child)

    def __len__(self):
        return len(self.routes)

    def __bool__(self):
        return True

    def __iter__(self):
        for name, route in self.routes.items():
            yield name, route

    def __repr__(self):
        return (
            '<{0} routes:{1}>'.format(
                get_qualified_name(self),
                len(self))
        )


class Choice(Base):
    """Search for a match to a route from multiple routers.
    """

    routers = None

    def __init__(self, *routers):
        self.routers = []
        for router in routers:
            if isinstance(router, Base):
                self.add_router(router)

    def add_route(self, route):
        raise NotImplementedError('Not used in a Choice router')

    def add_definition(self, definition):
        raise NotImplementedError('Not used in a Choice router')

    def add_router(self, router):
        """Adds another router type to be able to search through.
        """
        self.routers.append(router)

    def matches(self, request):
        """Match a request against all the routes.

        Args:
            request (watson.http.messages.Request): The request to match.

        Returns:
            A list of RouteMatch namedtuples.
        """
        for router in self:
            for route_match in router.matches(request):
                yield route_match

    def match(self, request):
        """Match a request against all the routes and return the first match.

        Args:
            request (watson.http.messages.Request): The request to match.

        Returns:
            The RouteMatch of the route.
        """
        for route_match in self.matches(request):
            return route_match
        return None

    def assemble(self, route_name, **kwargs):
        """See: Base.assemble
        """
        for router in self:
            if route_name in router:
                return router.routes[route_name].assemble(**kwargs)
        raise KeyError('No route named {0} can be found.'.format(route_name))

    # Internals

    def __getitem__(self, class_):
        """Retrieve a specific router instance from associated routers.

        Usage:

            .. code-block: python

            router = routers.Choice(routers.Dict())
            dict_router = routers[routers.Dict]
        """
        for router in self:
            if router.__class__ is class_:
                return router
        return None

    def __len__(self):
        return len(self.routers)

    def __bool__(self):
        return True

    def __iter__(self):
        for router in self.routers:
            if router:
                yield router

    def __repr__(self):
        return (
            '<{0} routers:{1}>'.format(
                get_qualified_name(self),
                len(self))
        )


class List(Base):
    """Creates routes from a list of routes.

    Priority will automatically be assigned based upon the order of the route
    definitions in the list.
    """
    def __init__(self, routes=None, build_strategies=None):
        super(List, self).__init__(routes, build_strategies)
        if not routes:
            routes = []
        for priority, route_definition in enumerate(routes):
            is_route = isinstance(route_definition, BaseRoute)
            if not is_route:
                if 'priority' not in route_definition:
                    route_definition['priority'] = priority
                self.add_definition(route_definition)
        self.sort()


class Dict(Base):
    """Create routes from a dictionary of route definitions.
    """
    def __init__(self, routes=None, build_strategies=None):
        super(Dict, self).__init__(routes, build_strategies)
        if not routes:
            routes = {}
        for name, route_definition in routes.items():
            is_route = isinstance(route_definition, BaseRoute)
            if not is_route:
                route_definition['name'] = name
                if 'path' not in route_definition:
                    route_definition['path'] = '/{}'.format(name)
                self.add_definition(route_definition)
        self.sort()

# Deprecated, will be removed in the next major version

ListRouter = List
DictRouter = Dict
ChoiceRouter = Choice
