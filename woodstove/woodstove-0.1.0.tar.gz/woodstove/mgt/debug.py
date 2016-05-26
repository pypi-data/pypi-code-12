import six
import time
from woodstove import app


class Debug(object):
    ''' Debugging endpoints '''

    wsapp = app.App('/debug')

    @wsapp.get('/apps')
    def apps(self):
        ''' Get list of loaded applications on this server instance. '''
        return {v.__class__.__name__:k for k,v in six.iteritems(self.wsapp.server.apps)}

    @wsapp.get('/routes')
    def routes(self):
        ''' Get list of loaded routs on this server instance. '''
        routes = {}
        for app in self.wsapp.server.apps.itervalues():
            routes[app.wsapp.path] = [
                {
                    "path": x.path, 
                    "method": x.method, 
                    "fname": x.fname
                } for x in app.routes
            ]
        return routes

    @wsapp.get('/time')
    def time(self):
        ''' Get current time '''
        return time.time()
