# -*- coding: utf-8 -*-

from __future__ import absolute_import

from collections import namedtuple

from flask import request

from rio_client.base import Client


class Current(namedtuple('Current', 'action project uuid')):
    pass

class Rio(object):
    """Flask extension for rio."""

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app, dsn=None):
        client_options = {}

        client_options['dsn'] = dsn or app.config.get('RIO_DSN')
        client_options['timeout'] = app.config.get('RIO_TIMEOUT')

        self.client = Client(**client_options)

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['rio'] = self


    def emit(self, action, payload):
        """Emit action."""
        return self.client.emit(action, payload)

    @property
    def current(self):
        """A namedtuple contains `uuid`, `project`, `action`.

        Example::

            @app.route('/webhook/broadcast-news')
            def broadcast_news():
                if rio.current.action.startswith('news-'):
                    broadcast(request.get_json())
        """
        event = request.headers.get('X-RIO-EVENT')
        data = dict([elem.split('=') for elem in event.split(',')])
        return Current(**data)
