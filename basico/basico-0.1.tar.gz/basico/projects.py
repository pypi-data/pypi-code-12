#!/usr/bin/python
# -*- coding: utf-8 -*-
# File: projects.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Projects service


from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import Pango
from datetime import datetime
from dateutil import parser as dateparser

from .service import Service


class Projects(Service):
    def initialize(self):
        self.get_services()
        self.setup_window()


    def setup_window(self):
        # setup widgets
        self.window = self.gui.add_widget('winProjects')
        self.parent = self.gui.get_widget('mainwindow')
        self.window.set_transient_for(self.parent)
        self.pname = self.gui.add_widget('etyProjectName')
        self.pname.connect('activate', self.add_project)
        self.boxproj = self.gui.add_widget('boxProjects')
        self.btnadd = self.gui.add_widget('btnAddProject')
        self.btnadd.connect('clicked', self.add_project)
        self.btndel = self.gui.add_widget('btnDelProject')
        self.btndel.connect('clicked', self.delete_project)
        self.btncancel = self.gui.add_widget('btnCancelProjects')
        self.btncancel.connect('clicked', self.hide_window)
        self.btnaccept = self.gui.add_widget('btnAcceptProjects')
        self.btnaccept.connect('clicked', self.link_to_project)
        self.treeview = self.gui.add_widget('trvprojwin', Gtk.TreeView())
        self.boxproj.add(self.treeview)
        self.hide_window()

        # setup model
        model = Gtk.ListStore(
            bool,           # CheckBox
            str             # Project name
        )
        self.treeview.set_model(model)

        # setup columns
        # Checkbox
        renderer = Gtk.CellRendererToggle()
        renderer.connect("toggled", self.on_cell_toggled)
        column = Gtk.TreeViewColumn('X', renderer, active=0)
        column.set_visible(True)
        column.set_expand(False)
        column.set_clickable(False)
        column.set_sort_indicator(False)
        self.treeview.append_column(column)

        # Project name
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn('Project name', renderer, text=1)
        column.set_visible(True)
        column.set_expand(True)
        column.set_clickable(True)
        column.set_sort_indicator(True)
        self.treeview.append_column(column)

        # Treeview features
        self.treeview.set_headers_visible(True)
        self.treeview.set_enable_search(True)
        self.treeview.set_grid_lines(Gtk.TreeViewGridLines.HORIZONTAL)
        self.treeview.set_search_column(1)
        self.treeview.connect('row-activated', self.double_click)
        selection = self.treeview.get_selection()
        selection.set_mode(Gtk.SelectionMode.SINGLE)
        self.treeview.set_search_entry(self.pname)


    def delete_project(self, *args):
        found = 0
        selection = self.treeview.get_selection()
        result = selection.get_selected()
        if result: #result could be None
            model, iter = result
            project = model.get_value(iter, 1)
            self.log.debug(project)
            sapnotes = self.sap.get_notes()
            for sapnote in sapnotes:
                projects = sapnotes[sapnote]['projects']
                if project in projects:
                    found += 1
            if found > 1:
                self.log.debug("Project %s is still assigned to other SAP Notes" % project)
                head = "Project could not be deleted"
                body = "Project %s is still assigned to other SAP Notes" % project
                self.uif.message_dialog(head , body)
            else:
                model.remove(iter)




    def add_project(self, *args):
        project = self.pname.get_text()
        model = self.treeview.get_model()

        found = False
        for row in model:
            if row[1].upper() == project.upper():
                found = True

        if not found and len(project) > 0:
            model.append([False, project])

        self.pname.set_text('')



    def show_window(self, sapnote=None):
        rootwin = self.gui.get_widget('mainwindow')
        self.window.set_transient_for(rootwin)
        self.load_projects(sapnote)
        self.window.set_no_show_all(False)
        self.window.show_all()

        #~ if sapnote is not None:
            #~ projects = self.sap.get_linked_projects(sapnote)
            #~ self.log.debug("Projects for SAP Note %s: %s" % (sapnote, projects))
            #~ dialog = Gtk.MessageDialog(self.parent, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Task completed")
            #~ dialog.format_secondary_text("All SAP Notes were downloaded sucessfully.")
            #~ dialog.run()
            #~ dialog.destroy()

    def hide_window(self, *args):
        self.window.set_no_show_all(True)
        self.window.hide()


    def get_services(self):
        self.gui = self.app.get_service("GUI")
        self.sap = self.app.get_service('SAP')
        self.uif = self.app.get_service('UIF')


    def double_click(self, treeview, row, col):
        model = treeview.get_model()
        self.pname.set_text(model[row][1])


    def populate(self, sapnotes):
        model = self.treeview.get_model()
        model.clear()
        #~ model.append([bool, str])


    def changed(self, *args):
        try:
            model, treeiters = self.selection.get_selected_rows()
            selected = set()
            if len(treeiters) > 0:
                for treeiter in treeiters:
                    if treeiter != None:
                        selected.add(model[treeiter][0])
            print (selected)

        except Exception as error:
            self.log.error (self.get_traceback())


    def on_cell_toggled(self, widget, path):
        model = self.treeview.get_model()
        model[path][0] = not model[path][0]


    def get_selected_notes(self):
        sapnoteview = self.gui.get_widget('sapnoteview')
        return sapnoteview.get_selected_notes()


    def link_to_project(self, *args):
        self.save_projects()
        self.hide_window()
        sapnotes = list(self.get_selected_notes())
        model = self.treeview.get_model()
        projects = []
        for row in model:
           link = row[0]
           if link == True:
                projects.append(row[1])

        sapnotes.sort()
        projects.sort()
        self.log.debug('SAP Notes: %s' % sapnotes)
        self.log.debug(' Projects: %s' % projects)
        self.sap.link_to_project(sapnotes, projects)
        sapnoteview = self.gui.get_widget('sapnoteview')
        sapnoteview.refresh()


    def get_all_projects(self):
        projects = []
        model = self.treeview.get_model()
        for row in model:
            projects.append(row[1])
        projects.sort()

        return projects


    def load_projects(self, sapnote=''):
        try:
            projects = self.get_config_value('Projects').split(',')
        except:
            projects = []
        model = self.treeview.get_model()
        model.clear()

        for project in projects:
            if len(project) > 0:
                if len(sapnote) > 0:
                    snprjs = self.sap.get_linked_projects(sapnote)
                    self.log.debug(snprjs)
                    if project in snprjs:
                        model.append([True, project])
                    else:
                        model.append([False, project])
                else:
                    model.append([False, project])


    def save_projects(self):
        settings = {}
        projects = self.get_all_projects()

        settings['Projects'] = ','.join(projects)
        self.config[self.section] = settings
        self.save_config()
