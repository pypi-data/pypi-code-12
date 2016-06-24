# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function
from . import SensorEvent
from tcell_agent.sanitize import SanitizeUtils
from future.backports.urllib.parse import urlsplit

class AppConfigSettings(SensorEvent):
  
    def __init__(self, package, section, name, value, prefix=""):
        super(AppConfigSettings, self).__init__("app_config_setting", ensure_delivery=True, queue_wait=True)
        self.setting(package, section, prefix, name, value)
    
    def setting(self, package, section, prefix, name, value):
        self["package"] = package
        self["section"] = section
        self["prefix"] = prefix
        self["name"] = name
        self["value"] = str(value)
        
