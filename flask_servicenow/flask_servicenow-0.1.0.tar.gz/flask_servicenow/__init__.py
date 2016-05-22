# -*- coding: utf-8 -*-


__author__ = "Robert Wikman <rbw@vault13.org>"

import servicenow_rest.api as sn
from flask import current_app

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


class ServiceNow(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

    def connect(self):
        return sn.Client(current_app.config['SN_INSTANCE'],
                         current_app.config['SN_USER'],
                         current_app.config['SN_PASS'])

    @property
    def connection(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'sn_client'):
                ctx.sn_client = self.connect()
            return ctx.sn_client

