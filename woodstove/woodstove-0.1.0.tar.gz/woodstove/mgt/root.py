from woodstove import app

class Root(object):
    wsapp = app.App('/', merge=True)

    @wsapp.get('/')
    def root(self):
        apps = self.wsapp.server.apps
        paths = []

        for app in apps.itervalues():
            ns = app.namespace if app.namespace != '/' else ''
            paths.append(''.join((ns, app.path)))

        return paths
