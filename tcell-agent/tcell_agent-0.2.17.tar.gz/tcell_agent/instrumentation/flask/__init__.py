# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function

from tcell_agent.agent import TCellAgent, PolicyTypes

import logging
logger = logging.getLogger('tcell_agent').getChild(__name__)
def _instrument():
    old_func = Flask.__init__
    def init(*args):
        TCellAgent.get_agent().ensure_polling_thread_running()
        return old_func(*args)
    Flask.__init__ = init

    old_process_response = Flask.process_response
    def process_response(self, response):
        result = old_process_response(self, response)
        csp_headers = TCellAgent.get_policy(PolicyTypes.CSP).headers()
        if csp_headers:
            for csp_header in csp_headers:
                response.headers[csp_header[0]] = csp_header[1]
        return result
    Flask.process_response = process_response

try:
    from flask.app import Flask
    if TCellAgent.tCell_agent:
        _instrument()
except Exception as e:
    logger.debug("Could not instrument flask")
