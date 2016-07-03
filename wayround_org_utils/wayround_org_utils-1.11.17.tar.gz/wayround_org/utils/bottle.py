
import bottle


class WSGIRefServer(bottle.ServerAdapter):

    def run(self, handler):

        import wsgiref.simple_server

        if self.quiet:

            class QuietHandler(wsgiref.simple_server.WSGIRequestHandler):

                def log_request(self, *args, **kw):
                    pass

            self.options['handler_class'] = QuietHandler

        self.srv = wsgiref.simple_server.make_server(
            self.host,
            self.port,
            handler,
            **self.options
            )

        self.srv.serve_forever()

        return
