#!/usr/bin/python
# -*- coding: utf-8 -*-
# File: settings.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Settings service


from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import Pango
from gi.repository.GdkPixbuf import Pixbuf

from .service import Service

class Settings(Service):
    def initialize(self):
        #~ self.gui = self.app.get_service('GUI')
        #~ sapnoteview = self.gui.get_widget('sapnoteview')
        view = self.get_config_value('View')
        #~ sapnoteview.set_view(view)
