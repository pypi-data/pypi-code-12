import os
import subprocess
import argparse
import json

from http.server import HTTPServer, SimpleHTTPRequestHandler


cwd = os.getcwd()


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ('/', '/termlib.js'):
            self.send_response(404)
            return
        os.chdir(os.path.dirname(__file__))
        super(Handler, self).do_GET()
        os.chdir(cwd)

    def do_POST(self):
        os.chdir(cwd)
        data = self.rfile.read(int(self.headers['Content-Length']))
        data = json.loads(data.decode('utf-8'))
        command = data.get('command')
        if not command:
            output = "%c(@orange)%Try `ls` to start with.%c()"
        else:
            output = self.get_command_output(command)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(output.encode('utf-8'))

    def get_command_output(self, command):
        try:
            data = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            data = e.output
        data = data.decode('utf-8')
        output = "%c(@olive)%" + data + "%c()"
        return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bind', '-b', default='', metavar='ADDRESS',
                        help='Specify alternate bind address '
                             '[default: all interfaces]')
    parser.add_argument('port', action='store',
                        default=8080, type=int,
                        nargs='?',
                        help='Specify alternate port [default: 8000]')
    args = parser.parse_args()

    httpd = HTTPServer((args.bind, args.port), Handler)
    print("serving at", args.bind, args.port)
    httpd.serve_forever()
