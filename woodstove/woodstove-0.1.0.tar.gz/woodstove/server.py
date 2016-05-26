import six
import bottle
from woodstove.app import App
from woodstove.log import loggable
from woodstove import conf


DEFAULT_APPS = conf.get('woodstove', 'apps', [
    'woodstove.mgt.root.Root', 
    'woodstove.mgt.debug.Debug',
    'woodstove.mgt.swagger.Swagger',
])


@loggable
class Server(object):
    host = None
    port = None

    def __init__(self):
        ''' '''
        self.root = bottle.default_app()
        self.namespaces = {}
        self.apps = {}

    def import_app(self, name):
        parts = name.split('.')
        cname = parts.pop()
        mname = '.'.join(parts)
        parts.pop(0)

        try:
            module = __import__(mname)
        except BaseException:
            self.logger.error("Unable to import app `%s`", name)

        for m in parts:
            module = getattr(module, m)

        klass = getattr(module, cname)
        appobj = klass()
        self.logger.info("Imported app %s as %r", name, appobj)
        return appobj

    def import_apps(self):
        for app in DEFAULT_APPS:
            self.mount(self.import_app(app))

    def get_namespace(self, name):
        return self.namespaces.setdefault(name, bottle.Bottle())

    def mount(self, app):
        if not isinstance(app, App):
            wsapp = app.wsapp
            if not isinstance(wsapp, App):
                raise TypeError("Invalid application attribute")
            oostyle = True
            name = app.__class__.__name__
        else:
            oostyle = False
            name = wsapp.path.lstrip('/').replace('/','_')

        namespace = self.get_namespace(wsapp.namespace)

        for route in wsapp.routes:
            if oostyle:
                meth = getattr(app, route.fname)
            else:
                meth = route.func

            self.logger.debug("Attaching route method %s.%s() at %s %s",
                              name, route.fname, route.path, route.method)
            wsapp.bottle_app.route(route.path, route.method, meth)

        self.logger.info("Mounting %s at %s", name, wsapp.path)
        wsapp.server = self
        self.apps[wsapp.path] = wsapp

        if wsapp.merge:
            namespace.merge(wsapp.bottle_app)
        else:
            namespace.mount(wsapp.path, wsapp.bottle_app)

        for prefix, bapp in six.iteritems(self.namespaces):
            if prefix == '/':
                self.root.merge(bapp)
            else:
                self.root.mount(prefix, bapp)

    def run(self, host=None, port=None):
        if host is None:
            host = 'localhost'

        if port is None:
            port = 8080

        self.host = host
        self.port = port
        self.root.run(host=host, port=port)
