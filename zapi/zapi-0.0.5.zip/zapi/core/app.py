__author__ = 'zhonghong'

import os
import json

# Python's bundled WSGI server
from wsgiref.simple_server import make_server

from zapi.core.common import Common
from zapi.core.logger import Logger
from zapi.core.route import Router

class App(Common):

    def __init__(self, app_path):
        super(App, self).__init__(app_path)
        self.app_path = app_path
        self.headers = []
        self.config = self._get_config
        self._init_logger()

    def _init_logger(self):
        if 'logfile' not in self.config.log:
            self.config.log['logfile'] = os.path.join(self.app_path, 'zapi.log')
        if 'loglevel' not in self.config.log:
            self.config.log['loglevel'] = 'INFO'
        self.log = Logger(**self.config.log)

    def add_header(self, key, value):
        self.headers.append((key.capitalize(), value))

    def application(self, environ, start_response):

        status, response_body = Router.route(self.app_path, environ)

        if not isinstance(response_body, basestring):
            response_body = json.dumps(response_body)

        if self.headers:
            response_headers = self.headers
        else:
            response_headers = [
                ('Content-Type', 'text/plain'),
                ('Content-Length', str(len(response_body)))
            ]
        start_response(status, response_headers)

        self.headers = []

        return [response_body]

    def serve_forever(self):
        # Instantiate the server
        host = self._get_config.server.get('host') or 'localhost'
        port = self._get_config.server.get('port') or 8080
        httpd = make_server(
            host, # The host name
            port, # A port number where to wait for the request
            self.application # The application object name, in this case a function
        )
        start_info = 'Serving on {host}:{port}'.format(host=host, port=port)
        print start_info
        self.log.info(start_info)

        # Serve forever
        httpd.serve_forever()

if __name__ == '__main__':

    app = App('')
    app.serve_forever()