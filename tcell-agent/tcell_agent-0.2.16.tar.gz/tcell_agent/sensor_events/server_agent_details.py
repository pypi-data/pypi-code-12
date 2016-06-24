# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function
from . import SensorEvent
from tcell_agent.sanitize import SanitizeUtils
from future.backports.urllib.parse import urlsplit

class ServerAgentDetailsEvent(SensorEvent):
    def __init__(self, 
        user=None, group=None, 
        language=None, language_version=None,
        framework=None, framework_version=None):
        super(ServerAgentDetailsEvent, self).__init__("server_agent_details")
        if user:
            self["user"] = user
        if group:
            self["group"] = group
        if language:
            self["language"] = language
        if language_version:
            self["language_version"] = language_version
        if framework:
            self["app_framework"] = framework
        if framework_version:
            self["app_framework_version"] = framework_version
