# -*- coding: utf-8 -*-

from __future__ import absolute_import

from rio_client.base import Client


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
