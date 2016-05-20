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
from tcell_agent.config import CONFIGURATION


def get_location_host(url):
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    return urlunsplit((scheme, netloc, "", "", ""))

class GlobalRequestMiddleware(object):
    _threadmap = {}

    @classmethod
    def get_current_request(cls):
      try:
        return cls._threadmap[threading.current_thread().ident]
      except Exception as e:
        pass

    def process_request(self, request):
        request._tcell_signals = {}
        request._tcell_context = TCellInstrumentationContext()

        def assign_route_id():
            urlconf = settings.ROOT_URLCONF
            set_urlconf(urlconf)
            resolver = get_resolver(urlconf)
            try:
                resolver_match = resolver.resolve(request.path_info)
            except:
                return                
            if resolver_match:
                route_table = get_route_table()
                request._tcell_context.route_id = route_table.get(resolver_match.func,{}).get("route_id")

        def better_ip_address():
            if CONFIGURATION.reverse_proxy != True:
                return request.META.get('REMOTE_ADDR','1.1.1.1')
            else:
                try:
                    reverse_proxy_header = CONFIGURATION.reverse_proxy_ip_address_header
                    if reverse_proxy_header is None:
                        reverse_proxy_header = "HTTP_X_FORWARDED_FOR" # This is the standard
                    else:
                        reverse_proxy_header = "HTTP_" + reverse_proxy_header.upper().replace('-','_')
                    x_forwarded_for = request.META.get(reverse_proxy_header,request.META.get('REMOTE_ADDR','1.1.1.1'))
                    if x_forwarded_for and x_forwarded_for != '':
                        ip = x_forwarded_for.split(',')[0].strip()
                    else:
                        ip = request.META.get('REMOTE_ADDR','1.1.1.1')
                    return ip
                except:
                    return request.META.get('REMOTE_ADDR','1.1.1.1')

        def initialize_request():
            request._tcell_context.transaction_id = str(uuid.uuid4())
            request._tcell_context.user_agent = request.META.get("HTTP_USER_AGENT")
            request._tcell_context.remote_addr = better_ip_address()


        def set_fullpath():
            request._tcell_context.fullpath = request.get_full_path()

        safe_wrap_function("Setting Transaction Id", initialize_request)
        safe_wrap_function("Setting Request FullPath", set_fullpath)
        safe_wrap_function("Assiging route ID to request (global)", assign_route_id)

        self._threadmap[threading.current_thread().ident] = request

    def process_exception(self, request, exception):
        try:
            del self._threadmap[threading.current_thread().ident]
        except KeyError:
            pass

    def process_response(self, request, response):
        safe_wrap_function("Check Location Header", self.checkLocationRedirect, request, response)
        safe_wrap_function("Insert CSP Headers", self.addCSP, request, response)
        safe_wrap_function("Insert Clickjacking Headers", self.addClickjacking, request, response)
        safe_wrap_function("Insert Secure Headers", self.addSecureHeaders, request, response)
        safe_wrap_function("Running Filters", self.run_filters, request, response)
        try:
            del self._threadmap[threading.current_thread().ident]
        except KeyError:
            pass        
        return response

    def run_filters(self, request, response):
        if(isinstance(response, HttpResponse)):
            response.content = request._tcell_context.filter_body(response.content)

    def addSecureHeaders(self, request, response):
        if TCellAgent.get_policy(PolicyTypes.SECURE_HEADERS):
            secure_headers = TCellAgent.get_policy(PolicyTypes.SECURE_HEADERS).headers()
            if secure_headers:
                for secure_header in secure_headers:
                    response[secure_header[0]] = secure_header[1]

    def addCSP(self, request, response):
        if(isinstance(response, HttpResponse) and response.has_header("Content-Type") ):
            if response["Content-Type"] and response["Content-Type"].startswith("text/html"):
                if TCellAgent.get_policy(PolicyTypes.CSP):
                    csp_headers = TCellAgent.get_policy(PolicyTypes.CSP).headers(
                        request._tcell_context.transaction_id,
                        request._tcell_context.route_id,
                        request._tcell_context.session_id,
                        request._tcell_context.user_id)
                    if csp_headers:
                        for csp_header in csp_headers:
                            header_value = csp_header[1]
                            response[csp_header[0]] = header_value

    def addClickjacking(self, request, response):
        if TCellAgent.get_policy(PolicyTypes.CLICKJACKING):
            csp_headers = TCellAgent.get_policy(PolicyTypes.CLICKJACKING).headers(
                request._tcell_context.transaction_id,
                request._tcell_context.route_id,
                request._tcell_context.session_id,
                request._tcell_context.user_id)
            if csp_headers:
                for csp_header in csp_headers:
                    header_value = csp_header[1]
                    if (response.has_header(csp_header[0])):
                        response[csp_header[0]] =  response[csp_header[0]] + ", " + header_value
                    else:
                        response[csp_header[0]] = header_value


    def checkLocationRedirect(self, request, response):
        redirect_policy = TCellAgent.get_policy(PolicyTypes.HTTP_REDIRECT)

        if redirect_policy and response.get("location") and redirect_policy.enabled:
            response["location"] = redirect_policy.process_location(
                    request._tcell_context.remote_addr,
                    request.method,
                    request.get_host(),
                    request.get_full_path(), 
                    response.status_code, 
                    response.get("location"),
                    route_id=request._tcell_context.route_id)
 
    def handleFingerprint(self, request, response):
        #if TCellAgent.tCell_agent.httptx_policy.fingerprint.get("enabled") and \
        event = FingerprintSensorEvent(request, session_id)
        TCellAgent.tCell_agent.addEvent(event)


    def handleLoginSuccessfulSignal(self, request, response):
        if TCellAgent.get_policy(PolicyTypes.HTTP_TX).auth_framework.get("enabled") and \
        request._tcell_sensors_httpx.get("login_attempt"):
            event = LoginSuccessfulSensorEvent(request, response)
            TCellAgent.send(event)

    def handleLoginFailureSignal(self, request, response):
        if TCellAgent.get_policy(PolicyTypes.HTTP_TX).auth_framework.get("enabled") and \
        request._tcell_sensors_httpx.get("login_attempt"):
            event = LoginFailureSensorEvent(request, response)
            TCellAgent.send(event)
            #elif TCellAgent.tCell_agent.httptx_policy.firehose.get("enabled"):
            #    content_type = response.get("content-type")
            #    if (content_type and content_type.lower().startswith("text/html")):
            #        logger.debug("firehose event")
            #        event = HttpTxSensorEvent(request, response)
            #        TCellAgent.tCell_agent.addEvent(event)