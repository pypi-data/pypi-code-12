# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
from django.conf.urls import patterns, include, url

try:
    import django
    from django.conf import settings
    settings.configure()
    settings.DATABASES = {
    'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'mydatabase',
    }
    }
    django.setup()
except RuntimeError:
    print("Django already setup")

from django.test import TestCase
from mock import patch
from django.http import HttpResponse

from mock import Mock
from .....instrumentation.django.middleware.globalrequestmiddleware import GlobalRequestMiddleware
from .....instrumentation.django.middleware.afterauthmiddleware import AfterAuthMiddleware
from .....instrumentation.django.middleware.body_filter_middleware import BodyFilterMiddleware
from django.middleware.common import CommonMiddleware
from .....config import CONFIGURATION
from .....agent import TCellAgent, PolicyTypes

from httmock import urlmatch, HTTMock
import requests
import json
from django.conf import settings

from django.test.client import RequestFactory

try:
    settings.configure()
except:
    pass
settings.DEFAULT_CHARSET = 'utf-8'


class BodyFilterMiddlewareTest(TestCase):
    _multiprocess_can_split_ = False

    def setUp(self):
        settings.ALLOWED_HOSTS = ['testserver','test.tcell.io']

        self.grm = GlobalRequestMiddleware()
        self.aam = AfterAuthMiddleware()
        self.cm = CommonMiddleware()
        self.bfm = BodyFilterMiddleware()

        rf = RequestFactory()
        self.request = rf.get('http://test.tcell.io/hello/')


        #self.request = Mock()
        self.request.session = Mock()
        self.request.session.session_key = "101012301200123"


        CONFIGURATION.version = 1
        CONFIGURATION.api_key = "Test_-ApiKey=="
        CONFIGURATION.app_id = "TestAppId-AppId"
        CONFIGURATION.host_identifier = "TestHostIdentifier"
        CONFIGURATION.uuid = "test-uuid-test-uuid"
        CONFIGURATION.fetch_policies_from_tcell = False

    def test_body_inject(self):
        def addEvent(self, event):
          event.post_process()

        TCellAgent.addEvent = addEvent
        TCellAgent.tCell_agent = TCellAgent()

        policy_json = {
            "csp-headers":{
              "policy_id":"nyzd", 
              "data":{
                "options":{
                  "js_agent_api_key":"000-000-1-2323"
                }
              }
            }
        }
        TCellAgent.tCell_agent.process_policies(policy_json, cache=False)

        self.grm.process_request(self.request)
        self.aam.process_request(self.request)
        self.cm.process_request(self.request)
        self.bfm.process_request(self.request)
        response =  HttpResponse("<html>\n<head>Title</head><body>hello world</body><html>",content_type="text/html")
        self.bfm.process_response(self.request, response)
        self.cm.process_response(self.request, response)
        self.aam.process_response(self.request, response)
        self.grm.process_response(self.request, response)
        expected = b"""<html>\n<head><script src="https://api.tcell.io/tcellagent.min.js" tcellappid="TestAppId-AppId" tcellapikey="000-000-1-2323"></script>Title</head><body>hello world</body><html>"""
        self.assertEqual(response.content, expected)
