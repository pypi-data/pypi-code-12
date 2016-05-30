#!/usr/bin/python
# -*- coding: utf-8 -*-
# File: gui.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: GUI module

import os
import sys
import subprocess

from datetime import datetime

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import Pango
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gio

from .service import Service
from .uiapp import UIApp


class GUI(Service):
    def initialize(self):
        '''
        Setup GUI Service
        '''
        # Invoke services
        self.sap = self.app.get_service('SAP')

        # Setup caches
        self.widgets = {} # Widget name : Object
        self.keys = {} # Key : Value; keys: doctype, property, values

        # Setup Glade builder
        self.setup_builder()


    def run(self):
        '''
        Let GUI service start
        '''
        self.log.debug("Setting up GUI")
        #~ Gdk.threads_init()

        GObject.threads_init()
        self.sap.run()
        self.ui = UIApp(self.app)
        self.ui.run()


    def quit(self, *args):
        '''
        GUI destroyed
        '''
        self.app.stop()


    def end(self):
        '''
        End GUI Service
        '''
        self.log.debug("GUI terminated")
        self.ui.quit()


    def setup_builder(self):
        '''
        Setup Gtk.Builder object
        '''
        DIR_UI = self.get_var('UI')
        self.builder = Gtk.Builder()
        self.builder.add_from_file(DIR_UI + 'basico.ui')


    def get_builder(self):
        '''
        Return Gtk.Builder object
        '''
        return self.builder()


    def swap_widget(self, parent, widget):
        '''
        Swap widget inside a container
        '''
        try:
            child = parent.get_children()[0]
            parent.remove(child)
            parent.add(widget)
            del (child)
        except:
            parent.add(widget)
        widget.show_all()


    def get_key(self, key):
        '''
        Return current value from var cache
        '''
        return self.keys[key]


    def set_key(self, key, value):
        '''
        Set current value for var cache
        '''
        self.keys[key] = value


    def add_widget(self, name, obj=None):
        '''
        Add widget to cache
        '''
        try:
            if obj is not None:
                self.widgets[name] = obj
            else:
                self.widgets[name] = self.builder.get_object(name)
            return self.widgets[name]
        except Exception as error:
            self.log.error (self.get_traceback())
            return None


    def get_widget(self, name):
        '''
        Return widget from cache
        '''
        try:
            return self.widgets[name]
        except KeyError:
            #~ self.log.error("Widget '%s' not found" % name)
            #~ return None
            return self.add_widget(name)


    def get_widgets(self):
        return self.widgets


    def get_app(self):
        return self.ui


    def get_window(self):
        return self.ui.get_window()
