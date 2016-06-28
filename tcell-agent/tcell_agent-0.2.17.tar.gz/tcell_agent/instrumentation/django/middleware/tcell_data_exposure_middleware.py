# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function

from tcell_agent.agent import TCellAgent, PolicyTypes
import os
from tcell_agent.sensor_events.httptx import HttpTxSensorEvent, FingerprintSensorEvent, LoginSuccessfulSensorEvent, LoginFailureSensorEvent
from tcell_agent.sensor_events.http_redirect import RedirectSensorEvent
import uuid
import re

from tcell_agent.sanitize import SanitizeUtils
from tcell_agent.instrumentation import handle_exception, safe_wrap_function

from future.backports.urllib.parse import urlsplit
from future.backports.urllib.parse import urlunsplit
from future.backports.urllib.parse import parse_qs

from tcell_agent.instrumentation.context import TCellInstrumentationContext

from django.http import HttpResponse
import time
import threading
import logging
logger = logging.getLogger('tcell_agent').getChild(__name__)

from django.conf import settings
from django.core.urlresolvers import get_resolver, set_urlconf
from tcell_agent.instrumentation.django.routes import get_route_table
import re
django_header_regex = re.compile('^HTTP_')

class TCellDataExposureMiddleware(object):

    def process_request(self, request):

        def form_dataex():
            dataloss_policy = TCellAgent.get_policy(PolicyTypes.DATALOSS)
            if dataloss_policy is None:
                return
            route_id = request._tcell_context.route_id
            def parameter_list(query_dict):
                for parameter in query_dict:
                    parameter_lower = parameter.lower()
                    actions = dataloss_policy.get_actions_for_form_parameter(parameter_lower, route_id)
                    if actions is None:
                        continue
                    parameter_values = query_dict.getlist(parameter,[])
                    for action in actions:
                        for parameter_value in parameter_values:
                            request._tcell_context.add_response_parameter_filter(parameter_value, action, parameter)
            parameter_list(request.GET)
            parameter_list(request.POST)

        def cookie_dataex():
            dataloss_policy = TCellAgent.get_policy(PolicyTypes.DATALOSS)
            if dataloss_policy is None:
                return
            route_id = request._tcell_context.route_id
            for cookie in request.COOKIES:
                actions = dataloss_policy.get_actions_for_cookie(cookie, route_id)
                if actions is None:
                    continue
                cookie_value = request.COOKIES.get(cookie)
                for action in actions:
                    request._tcell_context.add_response_cookie_filter(cookie_value, action, cookie)

        def header_dataex():
            dataloss_policy = TCellAgent.get_policy(PolicyTypes.DATALOSS)
            if dataloss_policy is None:
                return
            route_id = request._tcell_context.route_id
            headers = dict((django_header_regex.sub('', header), value) for (header, value) 
                        in request.META.items() if header.startswith('HTTP_'))
            for header in headers:
                actions = dataloss_policy.get_actions_for_header(header.lower(), route_id)
                if actions is None:
                    continue
                header_value = headers.get(header)
                for action in actions:
                    request._tcell_context.add_header_filter(header_value, action, header)

        safe_wrap_function("Data-Exposure for Request Forms", form_dataex)
        safe_wrap_function("Data-Exposure for Request Cookies", cookie_dataex)
        safe_wrap_function("Data-Exposure for Request Headers", header_dataex)

    def process_response(self, request, response):
        return response