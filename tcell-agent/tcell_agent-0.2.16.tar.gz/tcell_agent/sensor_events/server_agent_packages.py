# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function
from . import SensorEvent
from tcell_agent.sanitize import SanitizeUtils
from future.backports.urllib.parse import urlsplit

class ServerAgentPackagesEvent(SensorEvent):
    
    def __init__(self):
        super(ServerAgentPackagesEvent, self).__init__("server_agent_packages", ensure_delivery=True, flush_right_away=True)
        self.flush = True
        self.ensure = True
        self["packages"] = []
    
    def add_package(self, name, version, license=None):
        package = {
          "n":name, 
          "v":version,
          }
        if license is not None:
          package["l"] = license
        self["packages"].append(package)