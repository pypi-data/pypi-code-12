from tornado.web import URLSpec as url
from .views import IndexHandler

urls = [
    url(r"/", IndexHandler),
]
