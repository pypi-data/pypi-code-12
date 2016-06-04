
import SimpleHTTPServer

class HTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def init_response(self):
        if hasattr(self, 'is_response_inited'):
            return
        self.is_response_inited = True
        self.wfile.write("HTTP/1.0 200 OK\r\n")
        self.add_header('Date', self.date_time_string())

    def add_header(self, key, value):
        self.init_response()
        self.wfile.write(key + ': ' + str(value) + "\r\n")

    def set_content(self, content):
        self.init_response()
        self.add_header('Content-length', len(content))
        self.wfile.write("\r\n")
        self.wfile.write(content)
