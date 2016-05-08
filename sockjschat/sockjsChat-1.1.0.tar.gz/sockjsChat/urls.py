from tornado import web
from tornado.web import URLSpec as url
from sockjs.tornado import SockJSRouter

from settings import settings
from utils import include
from multiplex import MultiplexConnection
from apps.main.views import groupConnection, privateConnection
# Create multiplexer
router = MultiplexConnection.get(group=groupConnection, private=privateConnection)
print "router : ", router
# Register multiplexer
EchoRouter = SockJSRouter(router, '/chat')
# print "echorouter.ursl : ",EchoRouter.urls


urls = [
    url(r"/static/(.*)", web.StaticFileHandler, {"path": settings.get('static_path')}),
]
urls += include(r"/", "apps.main.urls")

urls = urls + EchoRouter.urls



