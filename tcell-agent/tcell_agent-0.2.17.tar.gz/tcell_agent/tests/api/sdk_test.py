from __future__ import unicode_literals
from __future__ import print_function

import unittest

from ...config import CONFIGURATION
from ...api import TCellAPI
from ...sensor_events import SensorEvent

from future.backports.urllib.parse import urlparse
from future.backports.urllib.parse import parse_qs

from httmock import urlmatch, HTTMock
import requests
import json

class CustomEvent(SensorEvent):
  def __init__(self):
    super(CustomEvent, self).__init__("chegg_custom_event")
    self["stuff"] = {
      "test2":["a","b","c"]
    }

class SDKTest(unittest.TestCase):

    def get_mock(self):
      @urlmatch(netloc=r'input\.tcell\.io$', path=r'^/api/v1/app/TestAppId-AppId/chegg_endpoint$')
      def tcell_mock(url, request):
        self.assertEqual(request.headers["Content-type"], "application/json")
        if request.headers["Authorization"] != "Bearer Test_-ApiKey==":
          return {'status_code':403}
        body_json = json.loads(request.body)
        events_json = body_json.get("chegg_events")
        if (events_json is None):
          return {'status_code': 300}
        if (events_json[0].get("stuff").get("test2") == ["a","b","c"] and
            events_json[0].get("event_type") == "chegg_custom_event" and
            body_json.get("hostname") == "TestHostIdentifier" and
            body_json.get("uuid") == "test-uuid-test-uuid"):
          return {'status_code': 200}
        return {'status_code': 404}
      return tcell_mock

    def chegg_test_ok(self):

        CONFIGURATION.version = 1
        CONFIGURATION.api_key = "Test_-ApiKey=="
        CONFIGURATION.app_id = "TestAppId-AppId"
        CONFIGURATION.host_identifier = "TestHostIdentifier"
        CONFIGURATION.uuid = "test-uuid-test-uuid"


        with HTTMock(self.get_mock()):
          c = CustomEvent()
          c["oh"] = {"more":"stuff"}
          response = TCellAPI.send_events([c], event_wrap_name="chegg_events", event_endpoint="chegg_endpoint")
          self.assertEqual(response.status_code, 200)

    def chegg_test_bad(self):
        CONFIGURATION.version = 1
        CONFIGURATION.api_key = "Test_-ApiKey=="
        CONFIGURATION.app_id = "TestAppId-AppId"
        CONFIGURATION.host_identifier = "TestHostIdentifier"
        CONFIGURATION.uuid = "test-uuid-test-uuid"

        with HTTMock(self.get_mock()):
          c = CustomEvent()
          response = TCellAPI.send_events([c], event_wrap_name="bad_wrapper", event_endpoint="chegg_endpoint")
          self.assertEqual(response.status_code, 300)

