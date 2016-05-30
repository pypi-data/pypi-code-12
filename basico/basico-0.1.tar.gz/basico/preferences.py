#!/usr/bin/python
# -*- coding: utf-8 -*-
# File: preferences.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Preferences service


from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import Pango
from gi.repository.GdkPixbuf import Pixbuf

from .service import Service

class Preferences(Service):
    def initialize(self):
        self.sap = self.get_service('SAP')
        self.gui = self.app.get_service('GUI')

        self.uiapp = self.gui.get_widget('uiapp')
