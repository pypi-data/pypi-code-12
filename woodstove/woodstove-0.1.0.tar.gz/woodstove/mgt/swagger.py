import socket
from woodstove import app

class Swagger(object):
    wsapp = app.App('/swagger')

    @wsapp.get('/api.json', formatter=None)
    def spec(self):
        paths = {}
        for app in self.wsapp.server.apps.itervalues():
            for route in app.routes:
                paths[(app.namespace + app.path + route.path).replace('//','/')] = {
                    route.method.lower(): {
                        "tags": [app.namespace],
                        "name": route.fname,
                        "description": route.func.__doc__,
                        "produces": ["application/json",],
                        "responses": {"200": {"description": "successful operation"}},
                    }
                }

        return {
                "swagger": "2.0",
                "info": {
                    "description": "Swagger docs",
                    "version": "1.0.0",
                    "title": "woodstove",
                },
                "host": socket.gethostname()+":"+str(app.server.port),
                "basePath": "/",
                "schemes": ["http"],
                "paths": paths,
        }
