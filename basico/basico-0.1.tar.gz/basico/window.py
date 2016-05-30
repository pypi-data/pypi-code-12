#!/usr/bin/python
# -*- coding: utf-8 -*-
# File: window.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Gtk.ApplicationWindow implementation

import os
import stat
import threading
import time
import platform

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')

from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import Pango
from gi.repository import WebKit
from gi.repository.GdkPixbuf import Pixbuf

from .log import get_logger
from .sapnoteview import SAPNoteView

#~ from .browser import WebBrowser

MONOSPACE_FONT = 'Lucida Console' if platform.system() == 'Windows' else 'monospace'

class GtkAppWindow(Gtk.ApplicationWindow):
    def __init__(self, uiapp):
        self.setup_controller(uiapp)
        self.get_services()
        self.gui.add_widget('uiapp', uiapp)
        self.gui.set_key('cmbvalue', 'search')
        self.settings = {}
        self.settings['fullscreen'] = False
        self.current_notes = {}

        self.setup_window()
        self.setup_widgets()
        self.setup_app()
        self.check_settings()


    def check_settings(self):
        # SAP module settings
        settings = self.sap.get_default_settings()
        for key in settings:
            try:
                self.sap.get_config_value(key)
            except:
                self.sap.set_config_value(key, settings[key])
                #~ self.log.warning("Setting '%s' does not exists" % setting)


    def setup_controller(self, uiapp):
        self.uiapp = uiapp
        self.controller = uiapp.get_controller()


    def setup_app(self):
        sapnoteview = self.gui.get_widget('sapnoteview')
        searchentry = self.gui.get_widget("stySearchInfo")
        viewlabel = self.gui.get_widget('lblViewCurrent')
        try:
            name = sapnoteview.get_view()
        except:
            name = 'components'
        sapnoteview.set_view(name)
        label = "<span size='20000'><b>%-10s</b></span>" % name.capitalize()
        viewlabel.set_markup(label)
        self.cb.refresh_view()
        searchentry.set_text('')
        self.cb.search_notes()
        sapnoteview.check_states()


    def setup_window(self):
        app_title = self.controller.get_app_info('name')
        Gtk.Window.__init__(self, title=app_title, application=self.uiapp)
        self.gui.add_widget('mainwindow', self)
        icon = self.im.get_icon('basico')
        self.set_icon(icon)
        # FIXME
        # From docs: Don’t use this function. It sets the X xlib.Window
        # System “class” and “name” hints for a window.
        # But I have to do it or it doesn't shows the right title. ???
        self.set_wmclass (app_title, app_title)
        self.set_role(app_title)
        #~ self.set_icon_from_file(self.env.get_var('ICONS') + '/basico.png')
        self.set_default_size(1024, 728)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        #~ self.connect('destroy', Gtk.main_quit)
        self.show_all()


    def setup_menu_views(self):
        # View label
        self.gui.add_widget('lblViewCurrent')

        ## Views Menu
        views_menu = self.gui.add_widget('mnuviews', Gio.Menu())

        # Last added view
        #~ TODO
        #~ views_menu.append_item(self.uif.create_item('View last added', 'app.view-lastadded', ''))
        #~ self.app.add_action(self.uif.create_action("view-lastadded", self.cb_show_dlnotes_window))

        # Most used view
        #~ TODO
        #~ views_menu.append_item(self.uif.create_item('View most used', 'app.view-mostused', ''))
        #~ self.app.add_action(self.uif.create_action("view-mostused", self.cb_show_dlnotes_window))

        # Tasks view
        views_menu.append_item(self.uif.create_item('View by tasks', 'app.view-tasks', 'emblem-system'))
        self.app.add_action(self.uif.create_action("view-tasks", self.cb.refresh_view, 'tasks'))

        # Projects view
        #~ views_menu.append_item(self.uif.create_item('View by projects', 'app.view-projects', ''))
        #~ self.app.add_action(self.uif.create_action("view-projects", self.cb.refresh_view, 'projects'))

        # Components view
        views_menu.append_item(self.uif.create_item('View by components', 'app.view-components', ''))
        self.app.add_action(self.uif.create_action("view-components", self.cb.refresh_view, 'components'))

        # Bookmarks view
        views_menu.append_item(self.uif.create_item('View bookmarks', 'app.view-bookmarks', ''))
        self.app.add_action(self.uif.create_action("view-bookmarks", self.cb.refresh_view, 'bookmarks'))


        # Annotations view
        #~ TODO
        #~ views_menu.append_item(self.uif.create_item('View by annotations', 'app.view-annotations', ''))
        #~ self.app.add_action(self.uif.create_action("view-annotations", self.cb_show_dlnotes_window))

        # Set menu model in button
        btnviews = self.gui.get_widget('mnuBtnViews')
        btnviews.set_menu_model(views_menu)


    def setup_menu_settings(self):
        ### SETTINGS POPOVER
        menu = Gio.Menu()
        #~ self.gui.add_widget("menu", menu)
        menu.append_item(self.uif.create_item('Fullscreen', 'app.settings-fullscreen', 'gtk-fullscreen'))
        menu.append_item(self.uif.create_item('Rename current project', 'app.project-rename', 'preferences-desktop-personal'))
        menu.append_item(self.uif.create_item('Refresh current project', 'app.project-refresh', 'view-refresh'))
        menu.append_item(self.uif.create_item('Close current project', 'app.project-close', 'window-close'))
        menu.append_item(self.uif.create_item('Delete current project', 'app.project-delete', 'list-remove'))
        menu.append_item(self.uif.create_item('Export current project', 'app.project-delete', 'document-save-as'))
        window = self.gui.get_window()
        window.set_app_menu(menu)
        app = self.gui.get_app()
        app.add_action(self.uif.create_item("settings-fullscreen"))

        #~ popover_action_group = Gio.SimpleActionGroup()
        btnsettings = self.gui.get_widget("mnuBtnViews")
        popover_settings = Gtk.Popover.new_from_model(btnsettings, menu)
        popover_settings.set_position(Gtk.PositionType.BOTTOM)
        btnsettings.connect('clicked', lambda _: popover_settings.show_all())


    def setup_menus(self):
        self.setup_menu_views()
        #~ self.setup_menu_actions()
        #~ self.setup_menu_settings()

    def show_home_page(self, *args):
        notebook = self.gui.get_widget('notebook')
        notebook.set_current_page(0)

    def show_settings_page(self, *args):
        sapnoteview = self.gui.get_widget('sapnoteview')
        sapnoteview.set_view('settings')
        notebook = self.gui.get_widget('notebook')
        notebook.set_current_page(2)

    def show_browser_page(self, *args):
        notebook = self.gui.get_widget('notebook')
        notebook.set_current_page(1)


    def show_search(self, *args):
        revsearch = self.gui.get_widget('revSearch')
        tgbsearch = self.gui.get_widget('tgbSearch')
        if tgbsearch.get_active():
            revsearch.set_reveal_child(True)
            revsearch.set_no_show_all(False)
            revsearch.show_all()
        else:
            revsearch.set_reveal_child(False)
            revsearch.set_no_show_all(True)
            revsearch.hide()


    def show_addsapnotes_dialog(self, *args):
        sapnoteview = self.gui.get_widget('sapnoteview')
        sapnoteview.set_view('download')
        notebook = self.gui.get_widget('notebook')
        notebook.set_current_page(1)


    def setup_widgets(self):
        self.mainbox = self.gui.get_widget('mainbox')
        self.mainbox.reparent(self)

        self.setup_menus()

        notesbox = self.gui.get_widget('notesbox')
        sapnoteview = SAPNoteView(self.controller)
        self.gui.add_widget('sapnoteview', sapnoteview)
        #~ self.log.debug("SAPNoteView widget added")
        self.gui.add_widget('combobox')
        search = self.gui.add_widget('stySearchInfo')
        #~ search.connect('search_changed', self.search_notes)
        search.connect('activate', self.cb.search_notes)
        self.setup_combobox()
        self.swap_widget(notesbox, sapnoteview)

        # Buttons
        btnabout = self.gui.get_widget('btnAbout')
        btnabout.connect('clicked', self.uiapp.cb_show_about)

        btnsettings = self.gui.get_widget('btnSettings')
        btnsettings.connect('clicked', self.show_settings_page)

        btnaddnote = self.gui.get_widget('btnStartDlNotes')
        btnaddnote.connect('clicked', self.cb.import_notes)

        refreshview = self.gui.get_widget('btnRefreshSAPNoteView')
        refreshview.connect('clicked', self.cb.refresh_and_clear_view)

        btnShowAddSAPNotesDlg = self.gui.get_widget('btnShowAddSAPNotesDlg')
        btnShowAddSAPNotesDlg.connect('clicked', self.show_addsapnotes_dialog)

        btnStopDlNotes = self.gui.get_widget('btnStopDlNotes')
        btnStopDlNotes.connect('clicked', self.cb.stop_dl_notes)

        tgbsearch = self.gui.get_widget('tgbSearch')
        tgbsearch.connect('toggled', self.show_search)
        revsearch = self.gui.get_widget('revSearch')
        revsearch.hide()
        revsearch.set_no_show_all(True)

        toggle= self.gui.get_widget('tgbFullScreen')
        toggle.connect('toggled', self.uif.fullscreen)
        switch = self.gui.get_widget('schExpandCollapse')
        switch.connect('state-set', sapnoteview.expand_collapse)
        switch = self.gui.get_widget('schSelectNotesAllNone')
        switch.connect('state-set', sapnoteview.select_all_none)

        button = self.gui.get_widget('btnQuit')
        button.connect('clicked', self.gui.quit)

        # Actions button
        button = self.gui.get_widget('mnuBtnActions')

        # Prefs for SAP module
        button = self.gui.add_widget('btnPrefsSAPApply')
        button.connect('clicked', self.cb.apply_preferences)

        button = self.gui.add_widget('btnPrefsSAPCancel')
        button.connect('clicked', self.cb.refresh_view)

        button = self.gui.add_widget('btnPrefsSAPReset')
        button.connect('clicked', self.sap.default_preferences)

        # Notebook Import Widget
        ntbimport = self.gui.add_widget('ntbAddSAPNotes')

        try:
            sap_settings = self.sap.get_custom_settings()
        except:
            self.log.error(self.controller.get_traceback())
            sap_settings = self.sap.get_default_settings()
            self.log.debug("SAP Default settings loaded")

        for setting in sap_settings:
            widget = self.gui.add_widget(setting)
            widget.set_text(sap_settings[setting])

        # Stats
        statsviewer = self.gui.add_widget('scrStatsViewer')

        btnstats = self.gui.add_widget('btnStatsByCompMain')
        btnstats.connect('clicked', self.cb.update_components_stats)
        iconwdg = self.gui.add_widget('imgStatsByCompMain')
        icon = self.im.get_pixbuf_icon('component', 64, 64)
        iconwdg.set_from_pixbuf(icon)

        btnstats = self.gui.add_widget('btnStatsByCategory')
        btnstats.connect('clicked', self.cb.update_categories_stats)
        iconwdg = self.gui.add_widget('imgStatsByCategory')
        icon = self.im.get_pixbuf_icon('category', 64, 64)
        iconwdg.set_from_pixbuf(icon)

        self.show_all()
        self.log.debug("GUI loaded")


    def __completion_func(self, completion, key, iter):
        model = completion.get_model()
        text = model.get_value(iter, 0)
        if key.upper() in text.upper():
            return True
        return False


    def setup_combobox_completions(self, key):
        model = Gtk.ListStore(str)
        search = self.gui.get_widget("stySearchInfo")
        completion = Gtk.EntryCompletion()
        completion.set_model(model)
        completion.set_text_column(0)
        completion.set_match_func(self.__completion_func)
        search.set_completion(completion)
        #~ self.log.debug("Completion Key: %s" % key)

        stats = self.sap.get_stats()

        try:
            items = list(stats[key])
            items.sort()
            for item in items:
                model.append([item])
        except:
            pass


    def cb_combobox_changed(self, combobox):
        model = combobox.get_model()
        treeiter = combobox.get_active_iter()
        key = model[treeiter][0]
        self.gui.set_key('cmbvalue', key)
        self.setup_combobox_completions(key)


    def setup_combobox(self):
        combobox = self.gui.get_widget('combobox')
        model = Gtk.TreeStore(str, str)
        combobox.set_model(model)

        ## key
        cell = Gtk.CellRendererText()
        cell.set_visible(False)
        combobox.pack_start(cell, True)
        combobox.add_attribute(cell, 'text', 0)

        ## value
        cell = Gtk.CellRendererText()
        cell.set_alignment(0.0, 0.5)
        combobox.pack_start(cell, expand=False)
        combobox.add_attribute(cell, 'markup', 1)
        combobox.connect('changed', self.cb_combobox_changed)

        model.append(None, ['search', 'Search in all database'])
        model.append(None, ['project', 'Filter by project name'])
        model.append(None, ['task', 'Filter by task name'])
        model.append(None, ['component', 'Filter by component'])
        model.append(None, ['category', 'Filter by category'])
        model.append(None, ['type', 'Filter by type'])
        model.append(None, ['id', 'Filter by Id'])
        model.append(None, ['title', 'Filter by title'])
        model.append(None, ['priority', 'Filter by priority'])
        model.append(None, ['version', 'Filter by version'])
        #~ model.append(None, ['released', 'Filter by release date'])

        combobox.set_active(0)


    def get_services(self):
        """Load services to be used in this class
        """
        self.gui = self.controller.get_service("GUI")
        self.app = self.gui.get_app()
        LOG_FILE = self.controller.get_file('LOG')
        self.log = get_logger('GtkAppWindow', LOG_FILE)
        self.sap = self.controller.get_service("SAP")
        self.uif = self.controller.get_service("UIF")
        self.prefs = self.controller.get_service("Settings")
        self.im = self.controller.get_service('IM')
        self.cb = self.controller.get_service('Callbacks')


    def swap_widget(self, container, combobox):
        """Shortcut to GUI.swap_widget method
        """
        self.gui.swap_widget(container, combobox)
