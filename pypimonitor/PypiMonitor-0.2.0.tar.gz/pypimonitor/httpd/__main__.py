# pypimonitor — An HTML dashboard to monitor your python packages
# Copyright (C) 2016 Louis Paternault
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from urllib.parse import urlparse, parse_qs
import http.server
import argparse
import pkg_resources
import os
import logging

import pypimonitor

LOGGER = logging.getLogger(pypimonitor.__name__)
DEFAULT_PORT = 8080
DEFAULT_HOST = ""

class HttpHandler(http.server.SimpleHTTPRequestHandler):

    yaml_dir = []

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _find_yaml(self, path):
        yaml = "{}.yaml".format(path)
        for directory in self.yaml_dir:
            if os.path.exists(os.path.join(directory, yaml)):
                return os.path.join(directory, yaml)

    def do_GET(self):
        path = urlparse(self.path).path.strip("/")
        if path in ['', 'index.html']:
            querydict = parse_qs(urlparse(self.path).query)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(pypimonitor.Renderer.from_args(
                packages=querydict.get('pkg'),
                cells=querydict.get('col', ["homepage", "pypiversion", "pypimdownloads", "pypiwdownloads", "pypiddownloads"]),
                users=querydict.get('user'),
                form={
                    'pkg': querydict.get('pkg', []),
                    'col': querydict.get('col', []),
                    'user': querydict.get('user', []),
                    'rooturl': '',
                    }
            ).render(), "utf-8"))
        elif self._find_yaml(path):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(pypimonitor.Renderer.from_yaml(
                self._find_yaml(path),
                form={'rooturl': "/".join(".."*len(path.split("/")))},
                ).render(), "utf-8"))
        else:
            super().do_GET()


def _type_address(text):
    partition = text.partition(":")
    if not partition[2]:
        return partition[0], DEFAULT_PORT
    try:
        return partition[0], int(partition[2])
    except ValueError:
        LOGGER.error("Argument '{}' is not a valid port number. Using '{}' instead.".format(partition[2], DEFAULT_PORT))
        return partition[0], DEFAULT_PORT
    return partition[0], DEFAULT_PORT

def _type_abspath(text):
    return os.path.abspath(text)

def commandline_parser():
    """Return a command line parser."""

    parser = argparse.ArgumentParser(
        prog="pypimonitor.httpd",
        description="A year calendar producer.",
        )

    parser.add_argument(
        '--version',
        help='Show version',
        action='version',
        version='%(prog)s ' + pypimonitor.VERSION
        )

    parser.add_argument(
        '-a', '--address',
        help='Server address and port, of the form HOST:PORT, HOST, :PORT.',
        nargs=1,
        type=_type_address,
        default=[(DEFAULT_HOST, DEFAULT_PORT)],
        )

    parser.add_argument(
        'dir',
        help='Directory containing yaml files to serve.',
        nargs='?',
        type=_type_abspath,
        default=".",
        )

    return parser

if __name__ == "__main__":
    arguments = commandline_parser().parse_args()
    HttpHandler.yaml_dir = [arguments.dir]
    os.chdir(os.path.join(pkg_resources.resource_filename(pypimonitor.__name__, 'data'), 'static'))
    server = http.server.HTTPServer(arguments.address[0], HttpHandler)
    if not arguments.address[0][0]:
        print("Serving HTTP on localhost port {} ...".format(arguments.address[0][1]))
    else:
        print("Serving HTTP on {} port {} ...".format(*arguments.address[0]))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()
