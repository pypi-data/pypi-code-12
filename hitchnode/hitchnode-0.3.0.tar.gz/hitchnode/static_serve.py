"""Static node server"""
from http.server import SimpleHTTPRequestHandler
from http.server import HTTPServer
from urllib import parse as urlparse
import optparse
import signal
import sys
import os


class Handler(SimpleHTTPRequestHandler):
    """
    HTTP handler for the static node files.
    """
    def do_GET(self):
        with open('index.html') as index_file_handle:
            url_params = urlparse.urlparse(self.path)
            if os.access('.{}{}'.format(
                os.sep, url_params.path), os.R_OK
            ):
                SimpleHTTPRequestHandler.do_GET(self)
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(index_file_handle.read().encode('utf8'))


def server(port_number=8080, directory="."):
    """Python library interface."""
    if port_number < 1024:
        sys.stderr.write("WARNING: Using a port below 1024 to run test Internet services"
                         " on is normally prohibited for non-root users, and usually inadvisable.\n\n")
        sys.stderr.flush()

    sys.stdout.write("Static node server running on port {} in directory {}\n".format(port_number, directory))
    sys.stdout.flush()

    os.chdir(directory)
    httpd = HTTPServer(('0.0.0.0', port_number), Handler)

    def signal_handler(signal, frame):
        print('')
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    httpd.serve_forever()


def main():
    """CLI interface."""
    parser = optparse.OptionParser()
    parser.add_option("-p", "--port", type="int", dest="http_port", default=8080,
                      help="Specify the port number for the static node server to run on (default: 8080).")

    parser.add_option("-d", "--directory", type="str", dest="serve_directory", default=".",
                      help="Specify directory to serve files from (default: current directory).")

    options, _ = parser.parse_args(sys.argv[1:])
    server(port_number=options.http_port, directory=options.serve_directory)


if __name__ == '__main__':
    main()
