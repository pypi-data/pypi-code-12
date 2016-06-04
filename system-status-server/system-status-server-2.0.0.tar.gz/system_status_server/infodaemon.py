
import time
import json
import SimpleHTTPServer
import BaseHTTPServer

from system_status_server.daemon import Daemon
from system_status_server.httphandler import HTTPHandler

from system_status_server.uptimeprovider import UptimeProvider
from system_status_server.loadprovider import LoadProvider
from system_status_server.cpuprovider import CPUProvider
from system_status_server.memoryprovider import MemoryProvider

providers = []

class AdvancedHTTPServer(BaseHTTPServer.HTTPServer):

    def __init__(self, listen, handler, request_timeout = 0):
        BaseHTTPServer.HTTPServer.__init__(self, listen, handler)
        self.request_timeout = request_timeout

    def set_request_timeout(self, value):
        self.request_timeout = value

    def finish_request(self, request, client_address):
        request.settimeout(self.request_timeout)
        # "super" can not be used because BaseServer is not created from object
        BaseHTTPServer.HTTPServer.finish_request(self, request, client_address)

class InfoHTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):

        data = dict()

        for provider in providers:
            data.update(provider.fetch())

        content = json.dumps(data)

        self.send_response(200)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

class InfoServer(object):
    def __init__(self, config):

        self.config = config

        if 'listen' not in self.config:
            print("'listen' node not found in the config")
            self.config = None

        if 'port' not in self.config['listen']:
            print("'port' value not found in the listen node")
            self.config = None


    def serve(self):

        providers.append(UptimeProvider())
        providers.append(LoadProvider())
        providers.append(CPUProvider())
        providers.append(MemoryProvider())

        address = self.config['listen']['address'] if 'address' in self.config['listen'] else '0.0.0.0'
        port = self.config['listen']['port']

        httpd = AdvancedHTTPServer((address, port), InfoHTTPHandler, 10)
        httpd.serve_forever()

class InfoDaemon(Daemon):
    def __init__(self, pid_file, config, log_file = '/dev/null'):

        self.server = InfoServer(config)

        if self.server.config is None:
            return

        super(InfoDaemon, self).__init__(pid_file, '/dev/null', log_file, log_file)

    def run(self):

        if self.server.config is None:
            return

        self.server.serve()
