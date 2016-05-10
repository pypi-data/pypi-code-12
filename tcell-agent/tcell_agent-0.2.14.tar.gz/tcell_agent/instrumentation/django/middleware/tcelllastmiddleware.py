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
from tcell_agent.appsensor.django import django_request_appsensor, django_response_appsensor
from django.core.urlresolvers import resolve
from tcell_agent.instrumentation.django.routes import get_route_table
from django.http import HttpResponse

import logging
import tcell_agent.tcell_logger
LOGGER = logging.getLogger('tcell_agent').getChild(__name__)


class TCellLastMiddleware(object):
    _threadmap = {}

    def process_request(self, request):
        safe_wrap_function("AppSensor Request", django_request_appsensor, request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        def assign_route_id():
            if request._tcell_context.route_id is None:
                if request.resolver_match:
                    route_table = get_route_table()
                    request._tcell_context.route_id = route_table.get(request.resolver_match.func,{}).get("route_id")
        safe_wrap_function("Assiging route ID to route (view)", assign_route_id)        
        return None

    def process_template_response(self, request, response):
        def assign_route_id():
            if request._tcell_context.route_id is None:
                if request.resolver_match:
                    route_table = get_route_table()
                    request._tcell_context.route_id = route_table.get(request.resolver_match.func,{}).get("route_id")
        safe_wrap_function("Assiging route ID to route (template)", assign_route_id)
        return response

    def process_response(self, request, response):
        def assign_route_id():
            if request.resolver_match:
                route_table = get_route_table()
                request._tcell_context.route_id = route_table.get(request.resolver_match.func,{}).get("route_id")
        if (request._tcell_context.route_id is None):
            safe_wrap_function("Assiging route ID to route (resp)", assign_route_id)        
        safe_wrap_function("AppSensor Response", django_response_appsensor, HttpResponse, request, response)
        return response
