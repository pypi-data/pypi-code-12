import click
from flask import Flask
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

import v1
from .settings import Config
from .sockethandler import handle_websocket
from .core.extensions import redis, db


def create_app(config=None):
    app = Flask(__name__, static_folder='static')
    if config:
        app.config.update(config)
    else:
        app.config.from_object(Config)
#    redis.init_app(app)
#    db.init_redis()

    app.register_blueprint(
        v1.bp,
        url_prefix='/v1')
    return app


def wsgi_app(environ, start_response):
    path = environ['PATH_INFO']
    if path == '/websocket':
        handle_websocket(environ['wsgi.websocket'])
    else:
        return create_app()(environ, start_response)


@click.command()
@click.option('-h', '--host_port', type=(unicode, int),
              default=('0.0.0.0', 5000), help='Host and port of server.')
@click.option('-r', '--redis', type=(unicode, int, int),
              default=('127.0.0.1', 6379, 0),
              help='Redis url of server.')
@click.option('-p', '--port_range', type=(int, int),
              default=(50000, 61000),
              help='Port range to be assigned.')
def manage(host_port, redis=None, port_range=None):
    Config.REDIS_URL = 'redis://%s:%s/%s' % redis
    Config.PORT_RANGE = port_range
    http_server = WSGIServer(host_port,
                             wsgi_app, handler_class=WebSocketHandler)
    print '----GLB Server run at %s:%s-----' % host_port
    print '----Redis Server run at %s:%s:%s-----' % redis
    http_server.serve_forever()
