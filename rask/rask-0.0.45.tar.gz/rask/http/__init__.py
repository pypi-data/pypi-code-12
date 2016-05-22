from rask.base import Base
from tornado.web import asynchronous,RequestHandler

__all__ = ['Handler']

class Handler(RequestHandler,Base):
    pass
