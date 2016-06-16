import sys
import traceback

from malibu.util import log

from bottle import response


def api_route(path="", actions=[], returns="text/plain"):
    """ decorator api_route(path="", actions=[], returns="text/plain")

        Sets values on route functions to automate
        loading routes into Bottle.
    """

    def api_route_outer(route_function):

        pre_execs = []

        if returns:
            def _set_return_type():
                response.content_type = returns

            pre_execs.append(_set_return_type)

        setattr(route_function, "route_func", True)
        setattr(route_function, "path", path)
        setattr(route_function, "actions", actions)
        setattr(route_function, "pre_exec", pre_execs)

        return staticmethod(route_function)
    return api_route_outer


def generate_bare_response():
    """ generate_bare_response()

        Generates a bare, generic "good" response.
    """

    response = {"status": 200}

    return response


def generate_error_response(code=500, exception=None, debug=False):
    """ generate_error_response(code=500, exception=None)

        Generates a dictionary with error codes and exception information
        to return instead of a bland, empty dictionary.

        The `code` parameter will set the status code in the response. If not
        provided, it defaults to 500.

        If exception is not provided, this method will return exception
        information based on the contents of sys.last_traceback
    """

    response = {"status": code}

    if debug:
        response.update({"stacktrace": {}})
        traceback_pos = 0
        for trace in traceback.extract_tb(sys.exc_info()[2], 4):
            response['stacktrace'].update({str(traceback_pos): ' '.join(trace)})
            traceback_pos += 1

    if exception:
        response.update({"exception": str(exception)})

    return response


class APIRouter(object):

    def __init__(self, manager):

        self.__log = log.LoggingDriver.find_logger()

        self.manager = manager
        self.app = self.manager.app

        self.routes = self.load_routes()

    def load_routes(self):
        """ load_routes(self)

            Loads route functions into Bottle based on the presence of
            extra variables in a function object.
        """

        routes = []

        for member in dir(self):
            member = getattr(self, member)
            if member and hasattr(member, "route_func"):
                self.__log.debug("Found routing function %s" % (member.__name__))
                routes.append(member)

        for route in routes:
            self.__log.debug("Routing %s requests to %s for path -> %s" % (
                route.actions, route.__name__, route.path))
            if route.pre_exec:
                def _pe_wrap(r):
                    route_handler = r

                    def _pe_internal(*args, **kw):
                        try:
                            [pef() for pef in route_handler.pre_exec]
                        except Exception:
                            self.manager.dsn.client.captureException()

                        return route_handler(*args, **kw)
                    return _pe_internal

                self.app.route(route.path, route.actions, _pe_wrap(route))
            else:
                self.app.route(route.path, route.actions, route)

        return routes
