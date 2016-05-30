#!/usr/bin/python
# -*- coding: utf-8 -*-
# File: tasks.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Tasks service


from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import Pango
from datetime import datetime
from dateutil import parser as dateparser

from .service import Service


class Tasks(Service):
    def initialize(self):
        self.get_services()
        self.setup_window()


    def setup_window(self):
        # setup widgets
        self.window = self.gui.add_widget('winTasks')
        self.window.connect('delete-event', self.hide_window)
        self.parent = self.gui.get_widget('mainwindow')
        #~ self.window.set_transient_for(self.parent)
        self.pname = self.gui.add_widget('etyTaskName')
        self.pname.connect('activate', self.add_task)
        self.boxtask = self.gui.add_widget('boxTasks')
        self.btnadd = self.gui.add_widget('btnAddTask')
        self.btnadd.connect('clicked', self.add_task)
        self.btndel = self.gui.add_widget('btnDelTask')
        self.btndel.connect('clicked', self.delete_task)
        self.btncancel = self.gui.add_widget('btnCancelTasks')
        self.btncancel.connect('clicked', self.hide_window)
        self.btnaccept = self.gui.add_widget('btnAcceptTasks')
        self.btnaccept.connect('clicked', self.link_to_task)
        self.treeview = Gtk.TreeView()
        self.gui.add_widget('trvtaskwin', self.treeview)
        self.boxtask.add(self.treeview)
        self.hide_window()

        # setup model
        model = Gtk.ListStore(
            bool,           # CheckBox
            str             # Task name
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

        # Task name
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn('Task name', renderer, text=1)
        column.set_visible(True)
        column.set_expand(True)
        column.set_clickable(True)
        column.set_sort_indicator(True)
        self.treeview.append_column(column)

        # Filters
        #Creating the filter, feeding it with the liststore model
        #~ self.task_filter = model.filter_new()
        #setting the filter function, note that we're not using the
        #~ self.task_filter.set_visible_func(self.task_filter_func)
        #~ self.task_filter.set_visible_column(1)

        # Treeview features
        self.treeview.set_headers_visible(True)
        self.treeview.set_enable_search(True)
        self.treeview.set_grid_lines(Gtk.TreeViewGridLines.HORIZONTAL)
        self.treeview.set_search_column(1)
        self.treeview.connect('row-activated', self.double_click)
        selection = self.treeview.get_selection()
        selection.set_mode(Gtk.SelectionMode.SINGLE)
        self.treeview.set_search_entry(self.pname)


    # row task visibility
    def task_row_visibility(self, model, iter, data):
        entry = self.gui.get_widget('etyTaskName')
        text = entry.get_text()

        return text.upper() in model.get_value(iter, 1)


    def task_filter_func(self, model, iter, data):
        """Tests if the task in the row is the one in the filter"""
        #~ self.log.debug(data)
        entry = self.gui.get_widget('etyTaskName')
        task = entry.get_text()

        #~ if len(task) == 0:
            #~ return False

        task_row = model[iter][1]

        if task.upper() in task_row.upper():
            return True
        else:
            return False


    def delete_task(self, *args):
        found = 0
        selection = self.treeview.get_selection()
        result = selection.get_selected()
        if result: #result could be None
            model, iter = result
            task = model.get_value(iter, 1)
            #~ self.log.debug(task)
            sapnotes = self.sap.get_notes()
            for sapnote in sapnotes:
                try:
                    tasks = sapnotes[sapnote]['tasks']
                    if task in tasks:
                        found += 1
                except:
                    pass
            if found > 1:
                self.log.warning("Task %s is still assigned to other SAP Notes" % task)
                head = "Task could not be deleted"
                body = "Task %s is still assigned to other SAP Notes" % task
                self.uif.message_dialog(head , body)
            else:
                model.remove(iter)




    def add_task(self, *args):
        task = self.pname.get_text()
        model = self.treeview.get_model()

        found = False
        for row in model:
            if row[1].upper() == task.upper():
                found = True

        if not found and len(task) > 0:
            model.append([False, task])

        self.pname.set_text('')



    def show_window(self, sapnotes=[]):
        rootwin = self.gui.get_widget('mainwindow')
        #~ self.window.set_transient_for(rootwin)
        self.load_tasks(sapnotes)
        self.window.set_no_show_all(False)
        self.window.show_all()
        self.window.set_keep_above(True)



    def hide_window(self, *args):
        self.window.set_no_show_all(True)
        self.window.hide()


    def get_services(self):
        self.gui = self.app.get_service("GUI")
        self.sap = self.app.get_service('SAP')
        self.uif = self.app.get_service('UIF')
        self.cb = self.app.get_service('Callbacks')


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


    def link_to_task(self, *args):
        self.save_tasks()
        self.hide_window()
        sapnotes = list(self.get_selected_notes())
        model = self.treeview.get_model()
        tasks = []
        for row in model:
           link = row[0]
           if link == True:
                tasks.append(row[1])

        sapnotes.sort()
        tasks.sort()
        #~ self.log.debug('SAP Notes: %s' % sapnotes)
        #~ self.log.debug(' Tasks: %s' % tasks)
        self.sap.link_to_task(sapnotes, tasks)
        self.cb.refresh_view(view='tasks')


    def get_all_tasks(self):
        tasks = []
        model = self.treeview.get_model()
        for row in model:
            tasks.append(row[1])
        tasks.sort()

        return tasks


    def load_tasks(self, sapnotes=[]):
        model = self.treeview.get_model()
        model.clear()
        try:
            alltasks = set(self.get_config_value('Tasks').split(','))
        except:
            alltasks = set()

        self.log.debug("All Tasks: %s" % alltasks)

        linkedtasks = set()
        for sapnote in sapnotes:
            tasks = self.sap.get_linked_tasks(sapnote)
            for task in tasks:
                linkedtasks.add(task)
        self.log.debug("Linked Tasks: %s" % alltasks)

        for task in alltasks:
            if task in linkedtasks:
                model.append([True, task])
            else:
                if len(task) > 0:
                    model.append([False, task])



    def save_tasks(self):
        settings = {}
        tasks = self.get_all_tasks()

        settings['Tasks'] = ','.join(tasks)
        self.config[self.section] = settings
        self.save_config()


    def save_tasks_from_stats(self, alltasks):
        settings = {}
        settings['Tasks'] = ','.join(alltasks)
        self.config[self.section] = settings
        self.save_config()
