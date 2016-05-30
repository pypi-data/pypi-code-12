#!/usr/bin/python
# -*- coding: utf-8 -*-
# File: uifuncs.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Generic UI functions service


from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import Pango
from gi.repository.GdkPixbuf import Pixbuf

from .service import Service

class UIFuncs(Service):
    def initialize(self):
        self.log.debug("Loading common UI Funcs service")
        self.gui = self.app.get_service('GUI')
        self.cb = self.app.get_service('Callbacks')
        self.im = self.app.get_service('IM')


    def get_label(self, text, xalign=0.5, yalign=0.5):
        label = Gtk.Label()
        label.set_selectable(False)
        label.set_markup(text)
        label.props.xalign = xalign
        label.props.yalign = yalign
        label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)

        return label


    def get_separator(self, draw=False, expand=False):
            separator = Gtk.SeparatorToolItem.new ()
            separator.set_expand(expand)
            separator.set_draw(draw)

            return separator


    def create_textview(self):
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        scrolledwindow.set_shadow_type(Gtk.ShadowType.IN)
        textview = Gtk.TextView()
        textbuffer = textview.get_buffer()
        textbuffer.set_text("This is some text inside of a Gtk.TextView. "
            + "Select text and click one of the buttons 'bold', 'italic', "
            + "or 'underline' to modify the text accordingly.")
        scrolledwindow.add(textview)

        return scrolledwindow


    def get_box(self):
        if Gtk.get_minor_version() < 14:
            return Gtk.Alignment()
        else:
            return Gtk.Box()


    def create_item(self, name, action, icon):
        item = Gio.MenuItem.new(name, action)
        if len(icon) > 0:
            item.set_icon(Gio.ThemedIcon.new(icon))
            #~ icon = self.im.get_themed_icon(icon)

        return item


    def create_action(self, name, callback=None, user_data=None):
        action = Gio.SimpleAction.new(name, None)

        if callback is None:
            window = self.gui.get_widget('mainwindow')
            action.connect('activate', self.cb.execute_action, user_data)
        else:
            action.connect('activate', callback, user_data)
        return action


    def message_dialog(self, head, body):
        dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "%s" % head)
        dialog.format_secondary_text("%s" % body)
        dialog.run()
        dialog.destroy()


    def fullscreen(self, switch, do_fullscreen=None):
        window = self.gui.get_widget('mainwindow')

        if do_fullscreen is None:
            #~ Get state from button:
            toggle = self.gui.get_widget('tgbFullScreen')
            do_fullscreen = toggle.get_active()

        if do_fullscreen == True:
            #~ window.fullscreen()
            window.maximize()
        else:
            #~ window.unfullscreen()
            window.unmaximize()


