# -*- coding: utf-8 -*-
from wsgiref.simple_server import make_server
from watson.dev.middleware import StaticFileMiddleware
from watson.dev.reloader import main


def make_dev_server(app, host='0.0.0.0', port=8000,
                    noreload=False, script_dir=None, public_dir=None):
    """
    A simple local development server utilizing the existing simple_server
    module, but allows for serving of static files.

    Never use this in production. EVER.

    Example:

    .. code-block:: python

        def my_app(environ, start_response):
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [b'<h1>Hello World!</h1>']

        if __name__ == '__main__':
            make_dev_server(my_app)

    Args:
        app: A WSGI callable
        host: The host to bind to
        port: The port
        noreload: Whether or not to automatically reload the application when
                  source code changes.
    """
    wrapped_app = StaticFileMiddleware(app, initial_dir=public_dir)
    if not noreload:
        main(__run_server, (wrapped_app, host, port), script_dir=script_dir)
    else:
        try:
            __run_server(wrapped_app, host, port)
        except KeyboardInterrupt:
            print('\nTerminated.')


def __run_server(app, host, port):
    print(
        'Serving application at http://{0}:{1} in your favorite browser...'.format(host, port))
    httpd = make_server(host, port, app)
    httpd.serve_forever()
