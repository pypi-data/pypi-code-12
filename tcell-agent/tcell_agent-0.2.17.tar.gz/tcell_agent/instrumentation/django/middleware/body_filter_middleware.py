# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved
from __future__ import unicode_literals
from __future__ import print_function
import unicodedata

from tcell_agent.config import CONFIGURATION
from tcell_agent.agent import TCellAgent, PolicyTypes

import os
from tcell_agent.sensor_events.httptx import HttpTxSensorEvent, FingerprintSensorEvent, LoginSuccessfulSensorEvent, LoginFailureSensorEvent
from tcell_agent.sensor_events.http_redirect import RedirectSensorEvent
import uuid
import re 

from tcell_agent.sanitize import SanitizeUtils
from tcell_agent.instrumentation import handle_exception, safe_wrap_function

from django.http import HttpResponse

class BodyFilterMiddleware(object):

    def add_tag(self, request, response):
        if(isinstance(response, HttpResponse) and response.has_header("Content-Type") ):
            if response["Content-Type"] and response["Content-Type"].startswith("text/html"):
                response_type = type(response.content)      
                tag_policy = TCellAgent.get_policy(PolicyTypes.CSP)
                if tag_policy and tag_policy.js_agent_api_key:
                    if CONFIGURATION.js_agent_api_base_url:
                        replace = "<head><script src=\"" + CONFIGURATION.js_agent_url + "\" tcellappid=\"" + CONFIGURATION.app_id + "\" tcellapikey=\"" + tag_policy.js_agent_api_key + "\" tcellbaseurl=\""+ CONFIGURATION.js_agent_api_base_url +"\"></script>"
                    else:
                        replace = "<head><script src=\"" + CONFIGURATION.js_agent_url + "\" tcellappid=\"" + CONFIGURATION.app_id + "\" tcellapikey=\"" + tag_policy.js_agent_api_key + "\"></script>"
                    #replace = u"test %s test" % str(tcell_agent.CONFIGURATION.js_agent_url)
                    if isinstance(response.content, str) == False:
                        replace = bytes(replace , "utf-8")
                    if response_type==str:
                        response.content = re.sub(b"<head>", replace, response.content.decode('utf8', 'ignore'))
                    else:
                        response.content = re.sub(b"<head>", replace, response.content)

    def process_request(self, request):
        pass

    def process_response(self, request, response):
        safe_wrap_function("Insert Body Tag", self.add_tag, request, response)        
        return response

