import logging

import sys

import os
import re
from flask import Flask, request, render_template
from os.path import join, abspath, dirname
from tornado.autoreload import watch
# import subfind_provider_opensubtitles
import subfind_provider_subscene

if getattr(sys, 'frozen', False):
    current_folder = abspath(dirname(sys.executable))
elif __file__:
    current_folder = abspath(os.path.dirname(__file__))


template_folder = join(current_folder, 'templates')
static_folder = abspath(join(current_folder, 'static'))

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)


@app.route('/')
def homepage():
    return "Hello World"

if __name__ == "__main__":
    from tornado import autoreload
    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop

    DEFAULT_APP_TCP_PORT = 5000

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s', )

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(DEFAULT_APP_TCP_PORT)
    ioloop = IOLoop.instance()
    autoreload.start(ioloop)

    root_dir = os.path.abspath(os.path.dirname(__file__))
    watch(join(root_dir, 'data/postgresql'))
    # watch(join(root_dir, 'generated'))

    ioloop.start()
