import inspect
import json
import logging
import os

import connexion
from flask.ext.compress import Compress
from flask.ext.cors import CORS

from flarecast.service.mini_json_encoder import MiniJSONEncoder
from flarecast.service.service_response import ServiceResponse


class FlarecastService(object):

    def __init__(self, service_name):
        self.service_name = service_name
        self.app = None

    @staticmethod
    def all_exception_handler(error):
        print('Error: %s' % error)
        return json.dumps({'message': error.message}), 500

    def create(self, **kwargs):
        logging.basicConfig(level=logging.INFO)
        is_debug = bool(os.environ.get("DEBUG", 1))

        # get name of caller for work dir
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])

        print("starting %s..." % self.service_name)
        app = connexion.App(
            mod.__name__,
            **kwargs
        )

        # set own default response class
        # to support direct passthrough
        app.app.response_class = ServiceResponse

        # set json encoder
        app.app.json_encoder = MiniJSONEncoder
        app.app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

        app.debug = is_debug

        # flask plugins
        Compress(app.app)
        CORS(app.app, expose_headers=["content-type, content-disposition"])

        # add error handler
        if not is_debug:
            app.app.register_error_handler(
                Exception, self.all_exception_handler)

        self.app = app

    def run(self, **kwargs):
        self.app.run(use_reloader=False, debug=self.app.debug, **kwargs)
