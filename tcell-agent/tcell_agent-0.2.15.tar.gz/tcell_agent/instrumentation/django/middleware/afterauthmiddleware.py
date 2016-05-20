# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function

from tcell_agent.agent import TCellAgent
import os
from tcell_agent.sensor_events.httptx import HttpTxSensorEvent, FingerprintSensorEvent, LoginSuccessfulSensorEvent, LoginFailureSensorEvent
from tcell_agent.sensor_events.http_redirect import RedirectSensorEvent
import uuid

from tcell_agent.sanitize import SanitizeUtils
from tcell_agent.instrumentation import handle_exception, safe_wrap_function

from future.backports.urllib.parse import urlsplit
from future.backports.urllib.parse import urlunsplit
from future.backports.urllib.parse import parse_qs

class AfterAuthMiddleware(object):
    def process_request(self, request):
        def add_user_and_session():
            try:
                if (hasattr(request, 'user') and request.user.is_authenticated() and request.user.id):
                    uid = request.user.id
                    if uid is not None:
                        uid = str(uid)
                    request._tcell_context.user_id = uid
            except:
                pass
            if (hasattr(request, 'session') and hasattr(request.session,'session_key')):
                request._tcell_context.raw_session_id = request.session.session_key
                request._tcell_context.session_id = SanitizeUtils.hmac_half(request.session.session_key)
        safe_wrap_function("Initizating Request", add_user_and_session)

    def process_response(self, request, response):
        return response