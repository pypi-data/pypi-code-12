# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function
from . import SensorEvent
from tcell_agent.sanitize import SanitizeUtils
from future.backports.urllib.parse import urlsplit

class HoneytokenSensorEvent(SensorEvent):
    def __init__(self,
        remote_addr,
        token_id
        ):
        super(HoneytokenSensorEvent, self).__init__("honeytoken")
        self["id"] = token_id
        self["remote_addr"] = remote_addr

    def post_process(self):
        pass