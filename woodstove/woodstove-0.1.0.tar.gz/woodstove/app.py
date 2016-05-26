import bottle
import functools
from woodstove import log
from woodstove import hooks
from woodstove import request
from woodstove import route
from woodstove import exhandler
from woodstove import context


@log.loggable
class App(object):
    '''
    
    :Example:

        class MyApp(object):
            wsapp = App('/foo')

            @wsapp.get('/')
            def foo(self):
                return "foobar"
    '''
    server = None

    def __init__(self, path, namespace=None, merge=False):
        '''
        Initialize this App instance, with the given ``path``, and optionally
        the given ``namespace``.

        :param path: Mount point for this application.
        :keyword namespace:
        :keyword merge: Merge the routes from this app into the parent application.
        '''
        self.bottle_app = bottle.Bottle()
        self.routes = []
        self.path = path

        if namespace is None:
            namespace = '/'

        self.namespace = namespace
        self.merge = merge

    def _load_args(self, req):
        body_args = None
        query_args = None

        if req.robj.body_args is not None:
            body_args = req.robj.body_args.validate(req.request.json)

        if req.robj.query_args is not None:
            query_args = req.robj.query_args.validate(req.request.query)

        return body_args, query_args

    def _do_auth(self, req):
        ''' '''
        if not req.robj.auth:
            return

        if req.robj.acl is not None:
            req.robj.acl.verify()

    @property
    def request(self):
        return context.ctx_get().get('request')

    def async(self):
        ''' Return a job record that has been passed to a worker '''
        raise NotImplementedError

    def route(self, path, method, **options):
        def decorator(func):
            robj = route.Route(path, method, func, options)
            hooks.call_hooks('route', 'setup', robj)
            self.routes.append(robj)
            
            @functools.wraps(func)
            def closure(*args, **kwargs):
                req = request.Request(robj, args, kwargs)
                ctx = {'request': req}
                hooks.call_hooks('route', 'context', ctx)

                with context.Context(**ctx):
                    hooks.call_hooks('route', 'enter', req)

                    try:
                        self._do_auth(req)
                        req.body, req.query = self._load_args(req)
                        self.logger.info("Calling: %s:%s(%r, %r)", robj.mname, robj.fname, args, kwargs)
                        req.ret = robj.func(*req.args, **req.kwargs)
                    except Exception as eobj:
                        req.exception = eobj
                        hooks.call_hooks('route', 'exception', req)

                        if not req.exception_handled:
                            exhandler.run_handler(req)
                    finally:
                        hooks.call_hooks('route', 'exit', req)

                    return req.formatter()

            closure.route = robj
            return closure
        return decorator

    def get(self, path, **options):
        return self.route(path, 'GET', **options)

    def post(self, path, **options):
        return self.route(path, 'POST', **options)

    def put(self, path, **options):
        return self.route(path, 'PUT', **options)

    def delete(self, path, **options):
        return self.route(path, 'DELETE', **options)

    def args(self, body=None, query=None):
        ''' '''
        def decorator(func):
            route = func.route
            route.body_args = body
            route.query_args = query
            return func
        return decorator

    def auth(self, acl=None):
        def decorator(func):
            route = func.route
            route.auth = True
            route.acl = acl.ACL(acl)
            return func
        return decorator
