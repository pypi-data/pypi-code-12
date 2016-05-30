#!/usr/bin/python
# -*- coding: utf-8 -*-
# File: menus.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Menus service


from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import Pango
from gi.repository.GdkPixbuf import Pixbuf

from .service import Service

class Menus(Service):
    def initialize(self):
        self.get_services()
        self.uiapp = self.gui.get_widget('uiapp')
        self.window = self.gui.get_widget('mainwindow')


    def get_services(self):
        self.gui = self.app.get_service('GUI')
        self.sap = self.app.get_service('SAP')
        self.cb = self.app.get_service('Callbacks')
        self.tasks = self.gui.get_service('Tasks')
        self.im = self.gui.get_service('IM')


    def create_popup_menu_by_task(self, task):
        #~ self.log.debug(task)
        menu = Gtk.Menu()
        ICONS_DIR = self.get_var('ICONS')
        sapnoteview = self.gui.get_widget('sapnoteview')

        item = Gtk.ImageMenuItem()
        icon = self.im.get_image_icon('task', 24, 24)
        item.set_image(icon)
        item.set_always_show_image(True)
        item.set_label("Select all SAP Notes on this task")
        item.connect("activate", self.select_by_task, task, True)
        menu.append(item)

        item = Gtk.ImageMenuItem()
        icon = self.im.get_image_icon('task', 24, 24)
        item.set_image(icon)
        item.set_always_show_image(True)
        item.set_label("Unselect all SAP Notes on this task")
        item.connect("activate", self.select_by_task, task, False)
        menu.append(item)

        return menu


    def select_by_task(self, menuitem, task, active):
        sapnoteview = self.gui.get_widget('sapnoteview')
        sapnoteview.select_by_task(task, active)


    def create_popup_menu_by_sapnote(self, sid):
        sapnote = self.sap.get_node(sid)
        sapnoteview = self.gui.get_widget('sapnoteview')
        component = sapnote['componentkey']
        category = sapnote['category']
        ICONS_DIR = self.get_var('ICONS')

        menu = Gtk.Menu()

        item = Gtk.ImageMenuItem()
        icon = self.im.get_image_icon('component', 24, 24)
        item.set_image(icon)
        item.set_always_show_image(True)
        item.set_label("Select all SAP Notes with component %s" % component)
        item.connect("activate", self.select_by_component, component, True)
        menu.append(item)

        return menu


    def create_popup_menu_by_component(self, component):
        #~ self.log.debug(component)
        menu = Gtk.Menu()
        ICONS_DIR = self.get_var('ICONS')
        sapnoteview = self.gui.get_widget('sapnoteview')

        item = Gtk.ImageMenuItem()
        icon = self.im.get_image_icon('component', 24, 24)
        item.set_image(icon)
        item.set_always_show_image(True)
        item.set_label("Select all SAP Notes on this component")
        item.connect("activate", self.select_by_component, component, True)
        menu.append(item)

        item = Gtk.ImageMenuItem()
        icon = self.im.get_image_icon('component', 24, 24)
        item.set_image(icon)
        item.set_always_show_image(True)
        item.set_label("Unselect all SAP Notes on this component")
        item.connect("activate", self.select_by_component, component, False)
        menu.append(item)

        return menu


    def select_by_component(self, menuitem, component, active):
        sapnoteview = self.gui.get_widget('sapnoteview')
        sapnoteview.select_by_component(component, active)


    def create_item(self, name, action, icon):
        item = Gio.MenuItem.new(name, action)
        item.set_icon(Gio.ThemedIcon.new(icon))
        return item


    def create_action(self, name, callback=None):
        action = Gio.SimpleAction.new(name, None)

        if callback is None:
            window = self.gui.get_widget('mainwindow')
            action.connect('activate', window.action_clicked)
        else:
            action.connect('activate', callback)
        return action


