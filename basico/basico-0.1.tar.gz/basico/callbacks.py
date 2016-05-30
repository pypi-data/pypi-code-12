#!/usr/bin/python
# -*- coding: utf-8 -*-
# File: callbacks.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: UI and related callbacks service

import os
import csv
import json

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import Pango
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import WebKit

from .service import Service

PROPKEYS = ['tasks', 'id', 'title', 'type', 'componentkey', 'componenttxt',
            'category', 'version', 'priority', 'language', 'releaseon',
            'bookmark']

class Callback(Service):
    def initialize(self):
        self.log.debug("Loading UI Callbacks")
        self.get_services()

    def get_services(self):
        self.gui = self.app.get_service('GUI')
        self.uif = self.app.get_service("UIF")
        self.sap = self.app.get_service('SAP')
        self.tasks = self.app.get_service('Tasks')
        self.alert = self.app.get_service('Notify')
        self.stats = self.app.get_service('Stats')

    def execute_action(self, *args):
        action = args[0]
        action_name = action.get_name()
        try:
            callback = "self.%s()" % action_name.replace('-', '_')
            return eval(callback)
        except Exception as error:
            self.log.error(error)
            self.log.error("Callback for action '%s' not registered" % action_name)
            raise


    def actions_browse(self, *args):
        sapnoteview = self.gui.get_widget('sapnoteview')
        sapnotes = list(sapnoteview.get_selected_notes())
        #~ sapnotes.sort()
        try:
            self.sap.browse_notes(sapnotes)
        except: pass


    def actions_other_delete(self, *args):
        sapnoteview = self.gui.get_widget('sapnoteview')
        sapnotes = list(sapnoteview.get_selected_notes())
        sapnotes.sort()
        winroot = self.gui.get_widget('mainwinow')

        dialog = Gtk.MessageDialog(winroot, 0, Gtk.MessageType.WARNING,
            Gtk.ButtonsType.OK_CANCEL, "Are you sure?")
        dialog.set_title("Deleting SAP Notes...")
        dialog.set_modal(True)
        dialog.set_transient_for(winroot)
        dialog.format_secondary_text(
            "These SAP Notes will be deleted:\n%s" % ', '.join(sapnotes))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            sapnotes = sapnoteview.get_selected_notes()
            for sapnote in sapnotes:
                self.sap.delete_sapnote(sapnote)
            self.search_notes()
            self.refresh_view()
            self.alert.show('Delete', 'Selected SAP Notes deleted', 'information')
            self.log.info("Selected SAP Notes deleted")
            self.sap.save_notes()
        elif response == Gtk.ResponseType.CANCEL:
            self.alert.show('Delete', 'Delete action canceled by user', 'warning')
            self.log.info("Delete action canceled by user")

        dialog.destroy()

        return response


    def actions_manage_tasks(self, *args):
        sapnoteview = self.gui.get_widget('sapnoteview')
        try:
            sapnotes = list(sapnoteview.get_selected_notes())
        except:
            sapnote = ''
        self.tasks.show_window(sapnotes)


    def actions_bookmark(self, *args):
        sapnoteview = self.gui.get_widget('sapnoteview')
        sapnotes = list(sapnoteview.get_selected_notes())
        view = sapnoteview.get_view()
        self.sap.set_bookmark(sapnotes)
        self.sap.save_notes()
        self.refresh_view(view=view)
        self.alert.show('Bookmarks', 'Selected SAP Notes bookmarked', 'information')


    def actions_unbookmark(self, *args):
        sapnoteview = self.gui.get_widget('sapnoteview')
        sapnotes = list(sapnoteview.get_selected_notes())
        self.sap.set_no_bookmark(sapnotes)
        self.sap.save_notes()
        self.refresh_view(view='bookmarks')
        self.alert.show('Bookmarks', 'Selected SAP Notes unbookmarked', 'information')


    def actions_export_csv(self, *args):
        rootwin = self.gui.get_widget('mainwndow')
        sapnoteview = self.gui.get_widget('sapnoteview')
        sapnotes = list(sapnoteview.get_selected_notes())
        dialog = Gtk.FileChooserDialog("Save file", rootwin,
            Gtk.FileChooserAction.SAVE,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            export_path = dialog.get_filename()
            writer = csv.writer(open(export_path, 'w'), delimiter=';', quoting=csv.QUOTE_ALL)
            csvrow = []
            for key in PROPKEYS:
                csvrow.append(key)
            writer.writerow(csvrow)
            for sapnote in sapnotes:
                csvrow = []
                props = self.sap.get_node(sapnote)
                for prop in PROPKEYS:
                    if prop == 'tasks':
                        tasks = ', '.join(props[prop])
                        csvrow.append(tasks)
                    else:
                        csvrow.append(props[prop])
                writer.writerow(csvrow)
            self.alert.show('Export', 'Selected SAP Notes exported successfully to CSV format', 'information')
            self.log.info("Selected SAP Notes exported to CSV format: %s" % export_path)
        else:
            self.alert.show('Export', 'Export canceled by user', 'warning')
            self.log.info("Export canceled by user")
        dialog.destroy()


    def actions_export_txt(self, *args):
        rootwin = self.gui.get_widget('mainwndow')
        sapnoteview = self.gui.get_widget('sapnoteview')
        sapnotes = list(sapnoteview.get_selected_notes())
        dialog = Gtk.FileChooserDialog("Save file", rootwin,
            Gtk.FileChooserAction.SAVE,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            export_path = dialog.get_filename()
            fout = open(export_path, 'w')
            for sapnote in sapnotes:
                fout.write("%s\n" % sapnote)
            self.alert.show('Export', 'Selected SAP Notes exported successfully to TXT format', 'information')
            self.log.info("Selected SAP Notes exported to TXT format: %s" % export_path)
        else:
            self.alert.show('Export', 'Export canceled by user', 'warning')
            self.log.info("Export canceled by user")
        dialog.destroy()


    def actions_export_bco(self, *args):
        rootwin = self.gui.get_widget('mainwndow')
        sapnoteview = self.gui.get_widget('sapnoteview')
        sapnotes = list(sapnoteview.get_selected_notes())
        dialog = Gtk.FileChooserDialog("Save file", rootwin,
            Gtk.FileChooserAction.SAVE,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            export_path = dialog.get_filename()
            bag = {}
            for sid in sapnotes:
                sapnote = self.sap.get_node(sid)
                bag[sid] = sapnote
            self.sap.save_notes(export_path, bag)
            self.alert.show('Export', 'Selected SAP Notes exported successfully to BCO format', 'information')
            self.log.info("Selected SAP Notes exported to BCO format: %s" % export_path)
        else:
            self.alert.show('Export', 'Export canceled by user', 'warning')
            self.log.info("Export canceled by user")
        dialog.destroy()



    def set_search_filter_key(self, key):
        self.gui.set_key('cmbvalue', key)


    def get_search_filter_key(self):
        cmbvalue = self.gui.get_key('cmbvalue')


    def set_search_term(self, term):
        searchentry = self.gui.get_widget("stySearchInfo")
        searchentry.set_text(term)


    def search_notes(self, *args):
        searchentry = self.gui.get_widget("stySearchInfo")
        cmbvalue = self.gui.get_key('cmbvalue')
        self.log.debug("Searching in %s" % cmbvalue)
        try:
            term = searchentry.get_text()
        except:
            term = ''
        self.log.debug("Looking for '%s'" % term)
        sapnoteview = self.gui.get_widget('sapnoteview')
        sapnotes = self.sap.get_notes()
        found = {}

        if len(term) == 0:
            self.current_notes = found = sapnotes
            sapnoteview.populate(found)
            sapnoteview.collapse()
            return

        if cmbvalue == 'search':
            for sid in sapnotes:
                if term.upper() in sapnotes[sid]['title'].upper():
                   found[sid] = sapnotes[sid]
        elif cmbvalue == 'project':
            for sid in sapnotes:
                try:
                    projects = sapnotes[sid]['projects']
                    for project in projects:
                        if term.upper() in project.upper():
                           found[sid] = sapnotes[sid]
                except: pass
        elif cmbvalue == 'task':
            #~ self.log.debug(sapnotes)
            for sid in sapnotes:
                try:
                    tasks = sapnotes[sid]['tasks']
                    for task in tasks:
                        if term.upper() in task.upper():
                           found[sid] = sapnotes[sid]
                except: pass
        elif cmbvalue == 'component':
            for sid in sapnotes:
                if term.upper() in sapnotes[sid]['componentkey'].upper():
                   found[sid] = sapnotes[sid]
                #~ if term.upper() in sapnotes[sid]['componenttxt'].upper():
                   #~ found[sid] = sapnotes[sid]
        elif cmbvalue == 'category':
            for sid in sapnotes:
                if term.upper() in sapnotes[sid]['category'].upper():
                   found[sid] = sapnotes[sid]
        elif cmbvalue == 'type':
            for sid in sapnotes:
                if term.upper() in sapnotes[sid]['type'].upper():
                   found[sid] = sapnotes[sid]
        elif cmbvalue == 'version':
            for sid in sapnotes:
                if term.upper() in sapnotes[sid]['version'].upper():
                   found[sid] = sapnotes[sid]
        elif cmbvalue == 'id':
            for sid in sapnotes:
                if term in sid:
                   found[sid] = sapnotes[sid]
        #~ elif cmbvalue == 'released':
            #~ for sid in sapnotes:
                #~ self.log.debug(sapnotes[sid]['reldate'].upper())
                #~ self.log.debug(sapnotes[sid]['releaseon'].upper())
                #~ if term.upper() in sapnotes[sid]['releaseon'].upper():
                   #~ found[sid] = sapnotes[sid]
            #~ Exact match
            #~ sid = "0"*(10 - len(term)) + term
            #~ self.log.debug("SAP Note id: %s" % sid)
            #~ found[sid] = sapnotes[sid]
        self.log.info("Term: '%s' (%d results)" % (term, len(found)))
        #~ if len(found) == 0:
            #~ found['XXXXXXXXXX'] = None
        self.current_notes = found
        self.log.debug("Current Notes: %d" % len(self.current_notes))
        sapnoteview.populate(found)
        #~ sapnoteview.expand()
        #~ self.refresh_view()


    def import_notes(self, entry):
        ntbimport = self.gui.get_widget('ntbAddSAPNotes')
        imptype = ntbimport.get_current_page() # 0 -> Download, 1 -> Import from file
        #~ self.log.debug(imptype)
        if imptype == 0:
            self.import_notes_from_sapnet()
        elif imptype == 1:
            self.import_notes_from_file()


    def import_notes_from_file(self):
        notebook = self.gui.get_widget('notebook')
        winroot = self.gui.get_widget('mainwinow')
        filechooser = self.gui.get_widget('fcwImportNotes')
        import_path = filechooser.get_filename()
        #~ self.log.debug(import_path)
        try:
            with open(import_path, 'r') as fp:
                bag = json.load(fp)
                self.sap.import_sapnotes(bag)
                self.log.info ("Imported %d notes from %s" % (len(bag), import_path))
            sapnoteview = self.gui.get_widget('sapnoteview')
            self.current_notes = bag
            sapnoteview.populate(bag)
            self.sap.save_notes()
            self.refresh_view()
            switch = self.gui.get_widget('schSelectNotesAllNone')
            sapnoteview.select_all_none(switch, True)
            sapnoteview.select_all_none(switch, False)
            sapnoteview.expand_all()
        except Exception as error:
            self.alert.show('Import', 'Nothing imported', 'error')
            self.log.warning("SAP Notes not found")



    def import_notes_from_sapnet(self):
        notebook = self.gui.get_widget('notebook')
        winroot = self.gui.get_widget('mainwinow')
        sapnotes = []
        bag = set()
        txtnotes = self.gui.get_widget('txtSAPNotes')
        textbuffer = txtnotes.get_buffer()
        istart, iend = textbuffer.get_bounds()
        lines = textbuffer.get_text(istart, iend, False)

        lines = lines.replace(',', '\n')
        sapnotes.extend(lines.split('\n'))

        for sapnote in sapnotes:
            if len(sapnote.strip()) > 0:
                bag.add(sapnote.strip())

        self.log.debug("%d SAP Notes to be downloaded: %s" % (len(bag), ', '.join(list(bag))))

        driver = self.sap.connect()
        if driver is None:
            dialog = Gtk.MessageDialog(winroot, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Task canceled")
            dialog.format_secondary_text("No suitable webdriver found. Check preferences.")
            dialog.run()
            dialog.destroy()

        resnotes = {}
        for sapnote in bag:
            rc = self.sap.download_note(sapnote, driver)
            resnotes[sapnote] = rc
        self.sap.build_stats()
        self.sap.logout(driver)

        textbuffer.set_text("")
        self.log.info("Task completed.")
        notebook.set_current_page(0)
        dialog = Gtk.MessageDialog(winroot, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Task completed")
        msgrc = ""
        ko = 0
        ok = 0
        for sapnote in resnotes:
            rc = resnotes[sapnote]
            if rc:
                ok += 1
            else:
                ko += 1
        msgrc += "Downloaded: %d\nErroneus: %d" % (ok, ko)
        self.alert.show('Download', msgrc, 'information')
        dlbag = {}
        mysapnotes = self.sap.get_notes()
        erroneus = set()
        for sid in bag:
            sid = "0"*(10 - len(sid)) + sid
            try:
                dlbag[sid] = mysapnotes[sid]
            except Exception as error:
                self.log.error(error)
                erroneus.add(sid)
        #~ self.log.error(erroneus)
        sapnoteview = self.gui.get_widget('sapnoteview')
        self.current_notes = dlbag
        sapnoteview.populate(dlbag)
        self.refresh_view()
        sapnoteview.expand_all()


    def stop_dl_notes(self, *args):
        notebook = self.gui.get_widget('notebook')
        txtSAPNotes = self.gui.get_widget('txtSAPNotes')
        buffer = txtSAPNotes.get_buffer()
        buffer.set_text("")
        notebook.set_current_page(0)
        self.refresh_view()
        self.alert.show('Download', 'Action canceled by user', 'warning')

    def refresh_and_clear_view(self, *args):
        switch = self.gui.get_widget('schSelectNotesAllNone')
        sapnoteview = self.gui.get_widget('sapnoteview')
        self.set_search_filter_key('search')
        self.set_search_term('')
        self.search_notes()
        self.refresh_view()
        sapnoteview.select_all_none(switch, False)
        sapnoteview.collapse()

    def refresh_view(self, action=None, callback=None, view=None):
        window = self.gui.get_widget('mainwindow')
        sapnoteview = self.gui.get_widget('sapnoteview')
        switch = self.gui.get_widget('schExpandCollapse')
        active = switch.get_active()
        if view is not None:
            viewlabel = self.gui.get_widget('lblViewCurrent')
            name = "<span size='20000'><b>%-10s</b></span>" % view.capitalize()
            viewlabel.set_markup(name)
            sapnoteview = self.gui.get_widget('sapnoteview')
            old_view = sapnoteview.get_view()
            sapnoteview.set_view(view)
            #~ self.log.debug("switching view from %s to %s" % (old_view, view))
            #~ sapnoteview.populate(self.current_notes)
            self.search_notes()
        #~ sapnoteview.expand_collapse(switch, active)
        sapnoteview.set_view(view)
        window.show_home_page()


    def setup_menu_actions(self):
        sapnoteview = self.gui.get_widget('sapnoteview')
        view = sapnoteview.get_view()
        #~ self.log.debug("View: %s" % view)
        ### ACTIONS POPOVER
        app = self.gui.get_app()

        ## Action Menu
        actions_menu = Gio.Menu()

        #~ # Browse SAP Notes
        actions_menu.append_item(self.uif.create_item('Browse SAP Note(s)', 'app.actions-browse', 'browse'))
        app.add_action(self.uif.create_action("actions-browse"))

        if view == 'bookmarks':
            #~ Unbookmark SAP Note(s) items
            actions_menu.append_item(self.uif.create_item('Unbookmark SAP Note(s)', 'app.actions-unbookmark', 'bookmark'))
            app.add_action(self.uif.create_action("actions-unbookmark"))
        else:
            #~ Bookmark SAP Note(s) items
            actions_menu.append_item(self.uif.create_item('Bookmark SAP Note(s)', 'app.actions-bookmark', 'bookmark'))
            app.add_action(self.uif.create_action("actions-bookmark"))

        # Manage task
        actions_menu.append_item(self.uif.create_item('Manage tasks', 'app.actions-manage-tasks', 'tasks'))
        app.add_action(self.uif.create_action("actions-manage-tasks"))

        # Export submenu
        actions_export_submenu = Gio.Menu()
        #~ Export to CSV
        actions_export_submenu.append_item(self.uif.create_item('Export as CSV', 'app.actions-export-csv', 'document-save'))
        app.add_action(self.uif.create_action("actions-export-csv"))
        #~ Export to TXT
        actions_export_submenu.append_item(self.uif.create_item('Export to plaint text', 'app.actions-export-txt', 'document-save'))
        app.add_action(self.uif.create_action("actions-export-txt"))
        #~ Export to BCO
        actions_export_submenu.append_item(self.uif.create_item('Export as Basico Package Object (BCO)', 'app.actions-export-bco', 'document-save'))
        app.add_action(self.uif.create_action("actions-export-bco"))
        actions_menu.append_submenu('Export', actions_export_submenu)
        #~ actions_menu.append_section('Export', actions_export_submenu)

        # Refresh SAP Notes
        #~ actions_menu.append_item(self.uif.create_item('Refresh selected SAP Notes', 'app.actions-other-refresh', 'refresh'))
        #~ app.add_action(self.uif.create_action("actions-other-refresh"))

        # Delete SAP Notes
        actions_menu.append_item(self.uif.create_item('Delete selected SAP Notes', 'app.actions-other-delete', 'delete'))
        app.add_action(self.uif.create_action("actions-other-delete"))

        # MnuButton valid with any modern version of Gtk (?> 3.10)
        btnactions = self.gui.get_widget('mnuBtnActions')
        btnactions.set_always_show_image(True)
        btnactions.set_property("use-popover", True)
        btnactions.set_menu_model(actions_menu)


    def apply_preferences(self, *args):
        self.sap.apply_preferences()
        notebook = self.gui.get_widget('notebook')
        notebook.set_current_page(0)
        self.refresh_view(view='tasks')
        self.alert.show('Settings', 'SAP preferences saved', 'information')


    def update_components_stats(self, *args):
        statsviewer = self.gui.get_widget('scrStatsViewer')
        view = WebKit.WebView()
        chart = self.stats.build_pie_maincomp()
        view.load_string(chart, 'text/html', 'UTF-8','/')
        self.gui.swap_widget(statsviewer, view)

    def update_categories_stats(self, *args):
        statsviewer = self.gui.get_widget('scrStatsViewer')
        view = WebKit.WebView()
        chart = self.stats.build_pie_categories()
        view.load_string(chart, 'text/html', 'UTF-8','/')
        self.gui.swap_widget(statsviewer, view)


    def test(self, *args):
        self.log.debug(args)


