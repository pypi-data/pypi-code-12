#########################################################################
#  The MIT License (MIT)
#
#  Copyright (c) 2014~2015 CIVA LIN (林雪凡)
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files
#  (the "Software"), to deal in the Software without restriction, including
#  without limitation the rights to use, copy, modify, merge, publish,
#  distribute, sublicense, and/or sell copies of the Software, and to
#  permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#  CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##########################################################################


import argparse

import bottle

from .. import command
from .. import app


class ServeCommand(command.Command):
    def get_name(self):
        return 'serve'

    def register_parser(self, subparsers):
        parser = subparsers.add_parser(
            self.get_name(),
            formatter_class=argparse.RawTextHelpFormatter,
            help='start a web server allow to remote access',
            description=(
                'start a web server allow webbrowser access'
                ' current lolinote project.\n\n'
                'The following options will overwrite the current config'
                ' settings.\n'
                'Use "loli config" to check the current config value.'))

        parser.add_argument(
            '-p', '--port', dest='port', metavar='PORT', type=str,
            help='assign a port for lolinote server')

        parser.add_argument(
            '-r', '--remote', dest='remote', action='store_true',
            help='allow remote access. make sure you really want to\n'
                 'expose your data server on network')

        parser.add_argument(
            '-d', '--debug', dest='debug', action='store_true',
            help='show more debug messages in browser.')

        parser.add_argument(
            '-s', '--ssl-cert-file', dest='ssl_cert_file',
            default=self.config[self.get_name()]['ssl_cert_file'],
            help='give a ssl certification to enable the ssl encrypt')

    def run(self, args):
        def ssl_process(ssl_cert_file, loliapp):
            def get_schema_and_server(ssl_cert_file):
                if ssl_cert_file:
                    class SSLWSGIRefServer(bottle.ServerAdapter):
                        def run(self, handler):
                            import wsgiref.simple_server
                            import ssl
                            if self.quiet:
                                class QuietHandler(
                                        wsgiref.
                                        simple_server.WSGIRequestHandler):
                                    def log_request(*args, **kw): pass
                                self.options['handler_class'] = QuietHandler
                            srv = wsgiref.simple_server.make_server(
                                self.host, self.port, handler, **self.options)
                            srv.socket = ssl.wrap_socket(
                                srv.socket,
                                certfile=args.ssl_cert_file,
                                server_side=True)
                            srv.serve_forever()

                    server = SSLWSGIRefServer(host=host, port=port)
                    schema = 'https'
                else:
                    server = bottle.WSGIRefServer(host=host, port=port)
                    schema = 'http'

                return schema, server

            def i_am_https(app):
                def https_app(environ, start_response):
                    environ['wsgi.url_scheme'] = 'https'
                    return app(environ, start_response)
                return https_app

            schema, server = get_schema_and_server(args.ssl_cert_file)
            if args.ssl_cert_file:
                loliapp = i_am_https(loliapp)
            return schema, server, loliapp

        self.require_rootdir()
        loliapp = app.get_loliapp(
            rootdir=self.rootdir,
            ignore_patterns=self.config['project']['ignore_patterns'],
            users=self.config[self.get_name()]['users'])

        port = args.port or self.config[self.get_name()]['port']
        if args.remote or self.config[
                self.get_name()].getboolean('allow_remote_access'):
            host = '0.0.0.0'
        else:
            host = '127.0.0.1'
        debug = args.debug or self.config[self.get_name()].getboolean('debug')

        schema, server, loliapp = ssl_process(args.ssl_cert_file, loliapp)

        print('Data folder is "{}".'.format(str(self.rootdir)))
        print('Lolinote server starting up...')
        print('Listening on {schema}://{host}:{port}'.format(
            schema=schema, host=host, port=port))
        print("Hit Ctrl-C to quit.\n")
        bottle.run(app=loliapp,
                   server=server, quiet=True, debug=debug)
