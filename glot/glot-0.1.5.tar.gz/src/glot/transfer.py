from aiohttp import web
import asyncio

_default_server_port = 18103


class OneFileHttpServer:
    def __init__(self, log, app, srv, handler, fut):
        self._app = app
        self._srv = srv
        self._handler = handler
        self._log = log
        self._fut = fut

    @classmethod
    @asyncio.coroutine
    def make(cls, log, filename):
        fut = asyncio.Future()

        def receive(request):
            log.debug('Got request')
            yield from request.post()
            try:
                with open(filename, 'wb') as f:
                    g = request.POST['file'].file
                    f.write(g.read())
                fut.set_result(filename)
            except:
                log.exception('Could not receive file')
                fut.set_result(None)

            return web.Response(body=b"Accepted")

        app = web.Application()
        log.debug('Adding POST route at /receive')
        app.router.add_route('POST', '/receive', receive)

        loop = asyncio.get_event_loop()
        handler = app.make_handler()

        # FIXME: this should be tied to the Docker interface,
        # when we have a good way of calculating it
        srv = yield from loop.create_server(handler, '0.0.0.0', _default_server_port)

        return cls(log, app, srv, handler, fut)

    def cancel(self):
        self._fut.cancel()

    @asyncio.coroutine
    def wait(self):
        yield from self._fut
        return self._fut.result()

    @asyncio.coroutine
    def close(self):
        self._srv.close()
        yield from self._srv.wait_closed()
        yield from self._app.shutdown()
        yield from self._handler.finish_connections(60.0)
        yield from self._app.cleanup()
