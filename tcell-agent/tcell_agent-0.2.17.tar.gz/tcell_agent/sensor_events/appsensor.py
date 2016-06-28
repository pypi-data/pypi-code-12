# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function
from . import SensorEvent
from ..appsensor import AppSensorMeta
from tcell_agent.sanitize import SanitizeUtils
from future.backports.urllib.parse import urlsplit

class AppSensorEvent(SensorEvent):
    def __init__(self,
        detection_point,
        parameter,
        location,
        remote_address,
        route_id,
        data,
        method,
        hmacd_session_id=None,
        user_id=None,
        count=None,
        payload=None,
        pattern=None):
        super(AppSensorEvent, self).__init__("as")
        self["dp"] = detection_point
        self["param"] = parameter
        self._raw_location = location
        self["remote_addr"] = remote_address
        self["rou"] = str(route_id)
        self["data"] = data
        self["m"] = method
        if user_id is not None:
            self["uid"] = str(user_id)
        if hmacd_session_id is not None:
            self["sid"] = str(hmacd_session_id)
        if count is not None:
            self["count"] = count
        if payload is not None:
            self["payload"] = payload[:150]
        if pattern is not None:
            self["pattern"] = pattern

    def post_process(self):
        if "payload" in self:
            self["payload"] = self["payload"][:150]
        if self._raw_location is not None:
            self["loc"] = SanitizeUtils.strip_uri(self._raw_location)
