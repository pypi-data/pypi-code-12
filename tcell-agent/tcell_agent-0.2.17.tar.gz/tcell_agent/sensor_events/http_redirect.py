# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function
from . import SensorEvent
from tcell_agent.sanitize import SanitizeUtils
from future.backports.urllib.parse import urlsplit

class RedirectSensorEvent(SensorEvent):
    def __init__(self,
        remote_addr,
        method,
        from_domain,
        from_full_path,
        status_code,
        redirect_url,
        user_id=None,
        session_id=None,
        route_id=None
        ):
        super(RedirectSensorEvent, self).__init__("redirect")
        self["method"] = method
        self["remote_addr"] = remote_addr
        self["from_domain"] = from_domain
        self.raw_full_path = from_full_path
        self["status_code"] = status_code
        self["to"] = redirect_url
        self.raw_user_id = user_id
        self.raw_session_id = session_id
        if route_id:
            self["rid"] = route_id

    def post_process(self):
        self["from"] = SanitizeUtils.strip_uri(self.raw_full_path)
        if (self.raw_user_id):
            self["uid"] = self.raw_user_id
        if (self.raw_session_id):
            self["sid"] = SanitizeUtils.hmac(self.raw_session_id)
