#!/usr/bin/python
# -*- coding: utf-8 -*-
# File: notify.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: notifications service

import sys
import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify

from .service import Service


class Notification(Service):
    def initialize(self):
        Notify.init('Basico')

    def show(self, module, message, icon_name):
        if sys.platform == 'win32':
            # Windows does not support Notify
            return

        icon = "dialog-%s" % icon_name # information | question | warning | error
        notification = Notify.Notification.new (module, message, icon)
        notification.show ()
