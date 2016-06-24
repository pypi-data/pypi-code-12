# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function
import unicodedata

from tcell_agent.agent import TCellAgent, PolicyTypes
import os
from tcell_agent.sensor_events.httptx import HttpTxSensorEvent, FingerprintSensorEvent, LoginSuccessfulSensorEvent, LoginFailureSensorEvent
from tcell_agent.sensor_events.http_redirect import RedirectSensorEvent
import uuid
import re 
import datetime

from tcell_agent.instrumentation import handle_exception, safe_wrap_function
import logging
import tcell_agent.tcell_logger
LOGGER = logging.getLogger('tcell_agent').getChild(__name__)

class TimerMiddleware(object):

    def process_request(self, request):
        def start():
            request._tcell_context.start_time = datetime.datetime.now()#
        safe_wrap_function("Start Request Timer", start)        

    def process_response(self, request, response):
        def stop():
            endtime = datetime.datetime.now()
            if request._tcell_context.start_time != 0:
                request_time = int((endtime - request._tcell_context.start_time).total_seconds() * 1000)
                TCellAgent.request_metric(
                    request._tcell_context.route_id, 
                    request_time, 
                    request._tcell_context.remote_addr,
                    request._tcell_context.user_agent,
                    request._tcell_context.session_id,
                    request._tcell_context.user_id
                )
                LOGGER.debug("request took {time}".format(time=request_time))
        safe_wrap_function("Stop Request Timer", stop)
        return response
