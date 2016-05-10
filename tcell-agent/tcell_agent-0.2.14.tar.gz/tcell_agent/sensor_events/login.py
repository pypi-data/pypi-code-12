# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function
from . import SensorEvent
from tcell_agent.sanitize import SanitizeUtils
from future.backports.urllib.parse import urlsplit

"""
"event_type":"login",
"event_name":"login-success",
"user_agent":"Mozilla/5.0 ...",
"referrer":"http://localhost:3085/users/sign_in",
"remote_addr":"10.0.2.2",
"header_keys":["VERSION","HOST","CONNECTION","CACHE_CONTROL","COOKIE"],
"user_id":"1",
"document_uri":"/users/sign_in",
"session":"e9e80cd52ad521ddb9090ac9ac",
"user_valid": true
"""

class LoginEvent(SensorEvent):
    def __init__(self):
        super(LoginEvent, self).__init__("login")
        self.raw_referrer = None
        self.raw_uri = None

    def success(self, *args, **kwargs):
        self["event_name"] = "login-success"
        return self._add_details(*args, **kwargs)

    def failure(self, *args, **kwargs):
        self["event_name"] = "login-failure"
        return self._add_details(*args, **kwargs)

    def _add_details(self,user_id, user_agent, referrer, remote_addr, header_keys, document_uri, session_id=None):
        if user_id:
            self["user_id"] = user_id
        self["user_agent"] = user_agent
        self.raw_referrer = referrer
        self["remote_addr"] = remote_addr
        self["header_keys"] = header_keys
        self.raw_uri = document_uri
        if session_id:
            self["session"] = session_id
        return self

    def post_process(self):
        if self.raw_uri is not None:
            #print(self.raw_uri)
            self["document_uri"] = SanitizeUtils.strip_uri(self.raw_uri)
        if self.raw_referrer is not None:
            #print(self.raw_referrer)
            self["referrer"] = SanitizeUtils.strip_uri(self.raw_referrer)

