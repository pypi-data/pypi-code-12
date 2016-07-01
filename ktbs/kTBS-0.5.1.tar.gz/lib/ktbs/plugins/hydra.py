from rdfrest.http_server import register_middleware, SESSION
from webob import Request, Response

from logging import getLogger

LOG = getLogger("ktbs")

class HydraMiddleware(object):
    """ Adds Hydra support to kTBS."""
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_reponse):
        req = Request(environ)
        resp = req.get_response(self.app)
        if req.method in {"GET", "HEAD"}:
            resp.headerlist.append(
                ("link",
                 '<http://liris.cnrs.fr/silex/2015/ktbs-hydra>; '
                 'rel="http://www.w3.org/ns/hydra/core#apiDocumentation"')
            )
        return resp(environ, start_reponse)

def start_plugin(config):
    register_middleware(SESSION,     HydraMiddleware)
    LOG.info("Hydra middleware started")

def stop_plugin():
    unregister_middleware(HydraMiddleware, True)
    LOG.info("Hydra middleware stopped")
