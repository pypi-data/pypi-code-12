# -*- coding: utf-8 -*-

"""
    flask_frink.connection
    ~~~~~~~~~~~~~~~~~~~~~~
    Handle setting up the DB in the Flasky way.
"""

from frink.connection import RethinkDB
from frink import frink

import logging
log = logging.getLogger(__name__)


class RethinkFlask(RethinkDB):

    def init_app(self, app):
        log.debug('RethinkFlask.init_app')
        self._app = app
        frink.init(
            host=app.config.get('RDB_HOST'),
            port=app.config.get('RDB_PORT'),
            db=app.config.get('RDB_DB')
        )

        # open connection before each request
        @app.before_request
        def before_request():
            self.connect()

        # close connection at end of each request
        @app.teardown_request
        def teardown_request(exception):
            self.disconnect()
