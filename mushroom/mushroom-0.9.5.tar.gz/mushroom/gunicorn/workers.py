from gevent.pywsgi import WSGIHandler
from geventwebsocket.handler import WebSocketHandler
from gunicorn.workers.ggevent import GeventPyWSGIWorker


class MushroomWebSocketHandler(WebSocketHandler):
    # FIXME implement a custom WebSocketHandler which does not accept any
    # websocket connection but only those with a valid session.
    pass


class MushroomWorker(GeventPyWSGIWorker):
    wsgi_handler = MushroomWebSocketHandler
