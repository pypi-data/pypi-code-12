import json

from tornado import gen, iostream
from tornado.web import Application, RequestHandler, RedirectHandler, StaticFileHandler
from tornado.websocket import WebSocketHandler
from tornado.ioloop import IOLoop
from mako.template import Template
from mako.lookup import TemplateLookup
import plim
import stylus

from .compat import Path
from .transformers import transform


here = Path(__file__).parent
PAGE_FORMAT_EXTS = ['.html', '.plim', '.md', '.rst']
site = None


def start_server(site_, port):
    global site, app
    site = site_

    if site.base_url != '/':
        handlers = [(r'/', RedirectHandler, {'url': site.base_url, 'permanent': False})]
    else:
        handlers = []
    handlers.extend([
        (r'/__reload.js', ReloadJSHandler),
        (r'/__reload__/', ReloadHandler),
        (site.base_url + r'(.*)', NoCacheFileHandler),
    ])
    app = Application(handlers, debug=True)
    app.sockets = set()
    app.listen(port)

    loop = IOLoop.current()
    send.loop = loop
    send.sockets = app.sockets
    loop.start()


def start_static_server(site_, port):
    settings = dict(
        path=str(site_.build_dir),
        default_filename='index.html',
    )
    app = Application([
        (site_.base_url + r'(.*)', StaticFileHandler, settings),
    ])
    app.listen(port)
    loop = IOLoop.current()
    loop.start()


class ReloadJSHandler(RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'text/javascript')
        reload_file = here / 'reload.js'
        self.write(reload_file.read_bytes())


class ReloadHandler(WebSocketHandler):
    def open(self):
        self.application.sockets.add(self)

    def on_close(self):
        self.application.sockets.remove(self)


class NoCacheFileHandler(RequestHandler):
    @gen.coroutine
    def get(self, path):
        self.set_header('Cache-Control', 'no-store')

        filepath = site.site_dir / path
        if filepath.is_dir():
            index_file = find_index_file(filepath)
            if index_file:
                filepath = index_file

        if not filepath.exists():
            self.clear()
            self.set_status(404)
            self.finish((site.site_dir / '404.html').read_bytes())
            return

        result = transform(filepath)
        if isinstance(result, tuple):
            mime_type, content = result
            self.set_header('Content-Type', mime_type)
            if mime_type == 'text/html':
                content = add_reload_snippet(content)
            self.finish(content)
            return

        content = get_content(filepath)
        for chunk in content:
            try:
                self.write(chunk)
                yield self.flush()
            except iostream.StreamClosedError:
                return


class SendCallable:
    """
    A callable object that is used to communicate with the browser.

    """

    def __init__(self):
        self.loop = None
        self.sockets = None

    def __call__(self, data):
        """
        It is safe to call this method from outside the main thread that is
        running the Tornado event loop.

        """
        if not self.loop:
            return
        self.loop.add_callback(self._send, data)

    def _send(self, data):
        "Write the given data to all connected websockets."
        for socket in self.sockets:
            socket.write_message(data)


send = SendCallable()


def find_index_file(dir):
    for ext in PAGE_FORMAT_EXTS:
        index_file = dir / ('index'+ext)
        if index_file.exists():
            return index_file
    return None


def get_content(path):
    with path.open('rb') as fp:
        remaining = None
        while True:
            chunk_size = 64 * 1024
            if remaining is not None and remaining < chunk_size:
                chunk_size = remaining
            chunk = fp.read(chunk_size)
            if chunk:
                if remaining is not None:
                    remaining -= len(chunk)
                yield chunk
            else:
                if remaining is not None:
                    assert remaining == 0
                return


def add_reload_snippet(html):
    index = html.find('</body>')
    if index == -1:
        return html
    else:
        return (html[:index] + '<script src="/__reload.js"></script>' +
                html[index:])
