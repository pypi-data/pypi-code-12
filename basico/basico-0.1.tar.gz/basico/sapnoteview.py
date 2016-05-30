#!/usr/bin/python
# -*- coding: utf-8 -*-
# File: sapnoteview.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: TreeView for SAP Notes

from cgi import escape
from enum import IntEnum
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import Pango
from datetime import datetime
from dateutil import parser as dateparser

from .log import get_logger

#~ Enum(value='Column', names=<...>, *, module='...', qualname='...', type=<mixed-in class>, start=1)
#~ Column = Enum('Column', 'rowtype checkbox icon id title component category type priority language released', start=0)

class Column(IntEnum):
    rowtype = 0
    checkbox = 1
    icon = 2
    id = 3
    title = 4
    component = 5
    category = 6
    type = 7
    priority = 8
    language = 9
    released = 10


class SAPNoteView(Gtk.TreeView):
    def __init__(self, app):
        self.app = app
        LOG_FILE = self.app.get_file('LOG')
        LOG_NAME = self.__class__.__name__
        self.log = get_logger(LOG_NAME, LOG_FILE)
        self.get_services()
        self.toggled = 0
        self.selected = set()
        self.count = 0

        try:
            self.view = self.settings.get_config_value('View')
        except:
            self.set_view('components')


        # Setup treeview and model
        Gtk.TreeView.__init__(self)
        self.model = Gtk.TreeStore(
            str,            # RowType
            bool,           # CheckBox
            Pixbuf,         # Icon
            str,            # Component key
            str,            # Category
            str,            # Type
            str,            # SAP Note Id
            str,            # Title
            str,            # Priority
            str,            # Language
            str             # Release date
        )
        self.set_model(self.model)

        # Setup columns
        # RowType
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn('', renderer, text=Column.rowtype.value)
        column.set_visible(False)
        column.set_expand(False)
        column.set_clickable(False)
        column.set_sort_indicator(False)
        self.append_column(column)

        # Checkbox
        renderer = Gtk.CellRendererToggle()
        renderer.connect("toggled", self.on_cell_toggled)
        column = Gtk.TreeViewColumn('X', renderer, active=1)
        column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column.set_visible(True)
        column.set_expand(False)
        column.set_clickable(False)
        column.set_sort_indicator(False)
        self.append_column(column)
        column.set_cell_data_func(renderer, self.cell_data_func)

        # Icon
        renderer = Gtk.CellRendererPixbuf()
        renderer.set_alignment(0.0, 0.5)
        self.column_icon = Gtk.TreeViewColumn('', renderer, pixbuf=2)
        self.column_icon.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_icon.set_visible(True)
        self.column_icon.set_expand(False)
        self.column_icon.set_clickable(False)
        self.column_icon.set_sort_indicator(False)
        self.append_column(self.column_icon)

        # Component key
        renderer = Gtk.CellRendererText()
        #~ renderer.set_property('ellipsize', Pango.EllipsizeMode.MIDDLE)
        self.column_component = Gtk.TreeViewColumn('SAP Notes', renderer, markup=3)
        self.column_component.set_visible(True)
        #~ self.column_component.set_expand(True)
        self.column_component.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_component.set_clickable(True)
        self.column_component.set_sort_indicator(True)
        self.column_component.set_sort_column_id(3)
        self.column_component.set_sort_order(Gtk.SortType.ASCENDING)
        self.append_column(self.column_component)
        expander_column = self.column_component


        # Category
        renderer = Gtk.CellRendererText()
        self.column_cat = Gtk.TreeViewColumn('Category', renderer, markup=4)
        self.column_cat.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_cat.set_visible(False)
        self.column_cat.set_expand(False)
        self.column_cat.set_clickable(True)
        self.column_cat.set_sort_indicator(True)
        self.column_cat.set_sort_column_id(4)
        self.column_cat.set_sort_order(Gtk.SortType.ASCENDING)
        self.append_column(self.column_cat)

        # Type
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn('Type', renderer, markup=5)
        column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column.set_visible(False)
        column.set_expand(False)
        column.set_clickable(True)
        column.set_sort_indicator(True)
        column.set_sort_column_id(5)
        column.set_sort_order(Gtk.SortType.ASCENDING)
        self.append_column(column)

        # SAP Note Id
        renderer = Gtk.CellRendererText()
        self.column_sid = Gtk.TreeViewColumn('SAP Note', renderer, markup=6)
        self.column_sid.set_visible(False)
        self.column_sid.set_expand(False)
        self.column_sid.set_clickable(True)
        self.column_sid.set_sort_indicator(True)
        self.column_sid.set_sort_column_id(6)
        self.column_sid.set_sort_order(Gtk.SortType.ASCENDING)
        self.append_column(self.column_sid)

        # Title
        renderer = Gtk.CellRendererText()
        renderer.set_property('ellipsize', Pango.EllipsizeMode.MIDDLE)
        self.column_title = Gtk.TreeViewColumn('Title', renderer, markup=7)
        self.column_title.set_visible(False)
        self.column_title.set_expand(True)
        self.column_title.set_clickable(True)
        self.column_title.set_sort_indicator(True)
        self.column_title.set_sort_column_id(7)
        self.column_title.set_sort_order(Gtk.SortType.ASCENDING)
        self.append_column(self.column_title)

        # Priority
        renderer = Gtk.CellRendererText()
        self.column_priority = Gtk.TreeViewColumn('Priority', renderer, markup=8)
        self.column_priority.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_priority.set_visible(True)
        self.column_priority.set_expand(False)
        self.column_priority.set_clickable(True)
        self.column_priority.set_sort_indicator(True)
        self.column_priority.set_sort_column_id(8)
        self.column_priority.set_sort_order(Gtk.SortType.ASCENDING)
        self.append_column(self.column_priority)

        # Language
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn('Language', renderer, markup=9)
        column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column.set_visible(False)
        column.set_expand(False)
        column.set_clickable(True)
        column.set_sort_indicator(True)
        column.set_sort_column_id(9)
        column.set_sort_order(Gtk.SortType.ASCENDING)
        self.append_column(column)

        # Release date
        renderer = Gtk.CellRendererText()
        self.column_rel = Gtk.TreeViewColumn('Released on', renderer, markup=10)
        self.column_rel.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_rel.set_visible(False)
        self.column_rel.set_expand(False)
        self.column_rel.set_clickable(True)
        self.column_rel.set_sort_indicator(True)
        self.column_rel.set_sort_column_id(10)
        self.column_rel.set_sort_order(Gtk.SortType.ASCENDING)
        self.append_column(self.column_rel)

        # TreeView common
        self.set_level_indentation(10)
        self.set_can_focus(True)
        self.set_headers_visible(False)
        self.set_enable_search(True)
        #~ self.set_rules_hint(True)
        #~ self.set_expander_column(expander_column)
        self.set_hover_selection(True)
        self.set_grid_lines(Gtk.TreeViewGridLines.NONE)
        self.set_search_entry(self.gui.get_widget('stySearchInfo'))
        self.set_search_column(3)
        #~ self.set_row_separator_func(self.row_separator_func)

        # Selection
        self.selection = self.get_selection()
        self.selection.set_select_function(self.select_function)
        self.selection.set_mode(Gtk.SelectionMode.BROWSE)

        # Go live
        self.connect('button_press_event', self.cb_button_press)
        self.connect('row-activated', self.double_click)
        self.connect('cursor-changed', self.row_changed)
        self.show_all()


    def cell_data_func(self, column, cell, store, iter, data=None):
        rowtype = store[iter][0]
        if rowtype != 'sapnote':
            cell.set_visible(False)
        else:
            cell.set_visible(True)


    def select_function(self, selection, store, path, current):
        return True

        #~ This code works: only allow select rows of type 'sapnote'
        #~ rowtype = store[path][0]
        #~ if rowtype == 'sapnote':
            #~ return True
        #~ else:
            #~ return False


    #~ def row_separator_func(self, model, iter):
        #~ """ Call user function to determine if this node is separator """
        #~ if iter and model.iter_is_valid(iter):
            #~ rowtype = model.get_value(iter, 0)
            #~ if row<type == 'sapnote':
                #~ return True
            #~ else:
                #~ return False
            #~ self.log.debug("Row type: %s" % rowtype)
            #~ return False
        #~ return False



    def get_services(self):
        self.gui = self.app.get_service("GUI")
        self.cb = self.app.get_service('Callbacks')
        self.menu = self.app.get_service("Menus")
        self.sap = self.app.get_service('SAP')
        self.im = self.app.get_service('IM')
        self.settings = self.app.get_service('Settings')
        self.plugins = self.app.get_service('Plugins')


    def row_changed(self, treeview):
        #~ button = self.gui.get_widget('mnuBtnActions')
        selected = set()
        selection = treeview.get_selection()
        model, treeiters = selection.get_selected_rows()


    def double_click(self, treeview, row, col):
        model = treeview.get_model()
        noteid = model[row][6]
        self.set_select_notes([noteid])
        #~ self.log.debug("Launching SAP Note %s in browser" % noteid)
        self.cb.actions_browse()


    def cb_button_press(self, treeview, event, data=None):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pthinfo = self.get_path_at_pos(x,y)
            if pthinfo is not None:
                path,col,cellx,celly = pthinfo
                self.grab_focus()
                self.set_cursor(path,col,0)

                model = treeview.get_model()
                treeiter = model.get_iter(path)
                rowtype = model.get_value(treeiter, 0)

                if rowtype == 'task':
                    task = model.get_value(treeiter, 6)
                    self.popup_menu = self.menu.create_popup_menu_by_task(task)
                elif rowtype == 'component':
                    component = model.get_value(treeiter, 6)
                    self.popup_menu = self.menu.create_popup_menu_by_component(component)
                elif rowtype == 'sapnote':
                    sid = model.get_value(treeiter, 6)
                    self.popup_menu = self.menu.create_popup_menu_by_sapnote(sid)
                else:
                    return False


                #~ noteid = model.get_value(treeiter, 6)
                #~ sapnote = self.sap.get_node(noteid)
                #~ self.log.debug("Selected SAP Note: %s" % sapnote)

                self.popup_menu.show_all()
                self.popup_menu.popup(None, None, None, None, event.button, event.time)
                return True # event has been handled


    def populate(self, sapnotes):
        #~ self.column_icon.set_visible(True)
        #~ self.column_component.set_visible(True)
        #~ self.column_title.set_visible(False)
        #~ self.column_cat.set_visible(False)

        self.log.debug("View '%s' populated with %d SAP Notes" % (self.view, len(sapnotes)))
        self.set_headers_visible(False)
        self.column_sid.set_visible(False)
        self.column_rel.set_visible(False)
        self.column_priority.set_visible(False)
        self.column_icon.set_visible(True)

        if self.view == 'components':
            self.populate_by_components(sapnotes)
        elif self.view == 'projects':
            self.populate_by_projects(sapnotes)
        elif self.view == 'tasks':
            self.populate_by_tasks(sapnotes)
        elif self.view == 'bookmarks':
            self.populate_by_bookmarks(sapnotes)
        else:
            self.populate_by_components(sapnotes)

        # Save last populated list of sap notes
        total = self.sap.get_total()
        notesid = set()
        for sapnote in sapnotes:
            notesid.add(sapnote)

        if len(notesid) < total:
            self.settings.set_config_value('Notes', ','.join(notesid))



    def populate_by_bookmarks(self, sapnotes):
        #~ self.log.debug('Populating bookmarks')
        self.model.clear()
        self.set_headers_visible(True)
        self.column_sid.set_visible(True)
        self.column_icon.set_visible(False)
        self.column_component.set_visible(True)
        self.column_component.set_expand(False)
        self.column_title.set_visible(True)
        self.column_priority.set_expand(False)
        self.column_cat.set_visible(False)
        #~ self.column_component.set_visible(False)
        #~ self.column_component.set_expand(False)
        self.column_component.set_title('Component')
        icon_bookmark = self.im.get_icon('bookmark')

        for sid in sapnotes:
            try:
                bookmark = sapnotes[sid]['bookmark'] # True or False
            except:
                bookmark = False

            if bookmark:
                sapnote = self.get_node_sapnote(sapnotes[sid], sid)
                self.model.append(None, sapnote)


    def get_node_project(self, project, icon):
        if project == '':
            title = "<span size='18000'><b>No project assigned</b></span>"
        else:
            title = "<span size='18000'><b>%s</b></span>" % project

        node = []
        node.append('project')
        node.append(0)
        node.append(icon)
        node.append(title) # Component
        node.append("") # Category
        node.append("") # Type
        node.append("") # Id
        node.append("") # Title
        node.append("") # Priority
        node.append("") # Lang
        node.append("") # Release on
        return node


    def get_node_task(self, task, icon):
        if task == '':
            title = "<span size='18000'><b>No task assigned</b></span>"
        else:
            title = "<span size='18000'><b>%s</b></span>" % task

        node = []
        node.append('task')
        node.append(0)
        node.append(icon)
        node.append(title) # Component
        node.append("") # Category
        node.append("") # Type
        node.append(task) # Id
        node.append("") # Title
        node.append("") # Priority
        node.append("") # Lang
        node.append("") # Release on
        return node


    def populate_by_projects(self, sapnotes):
        self.model.clear()
        treepids = {}
        icon_noproject = self.im.get_icon('noproject')
        icon_project = self.im.get_icon('project')
        icon_sapnote = self.im.get_icon('sapnote')
        icon_bookmark = self.im.get_icon('bookmark')
        self.column_component.set_title('Projects')

        if len(sapnotes) == 0:
            return

        node = self.get_node_project('', icon_noproject)
        pid = self.model.append(None, node)
        treepids['None'] = pid

        notlinked = 0
        for sid in sapnotes:
            try:
                projects = sapnotes[sid]['projects']
            except:
                projects = []


            if len(projects) == 0:
                #~ SAP Note not linked to any project
                sapnote = self.get_node_sapnote(sapnotes[sid], sid)
                self.model.append(treepids['None'], sapnote)
                notlinked += 1
            else:
                #~ SAP Note linked to projects
                for project in projects:
                    try:
                        pid = treepids[project]
                    except:
                        node = self.get_node_project(project, icon_project)
                        pid = self.model.append(None, node)
                        treepids[project] = pid

                    sapnote = self.get_node_sapnote(sapnotes[sid], sid)
                    self.model.append(pid, sapnote)

        if notlinked == 0:
            self.model.remove(treepids['None'])


    def populate_by_tasks(self, sapnotes):
        self.model.clear()
        treepids = {}
        icon_notask = self.im.get_icon('notask')
        icon_task = self.im.get_icon('task')
        icon_sapnote = self.im.get_icon('sapnote')
        icon_bookmark = self.im.get_icon('bookmark')
        self.column_component.set_title('Tasks')

        if len(sapnotes) == 0:
            return

        #~ "No task assigned" node creation
        node = self.get_node_task('', icon_notask)
        pid = self.model.append(None, node)
        treepids['None'] = pid

        scomp = set()
        dcomp = {}
        taskset = set()
        for sid in sapnotes:
            try:
                # setup components
                compkey = escape(sapnotes[sid]['componentkey'])
                comptxt = escape(sapnotes[sid]['componenttxt'])
                scomp.add(compkey)
                dcomp[compkey] = comptxt

                # setup tasks
                for task in sapnotes[sid]['tasks']:
                    taskset.add(task)
            except: pass

        lcomp = list(scomp)
        lcomp.sort()

        tasklist = []
        tasklist.extend(taskset)
        tasklist.sort()

        for task in tasklist:
            node = self.get_node_task(task, icon_task)
            pid = self.model.append(None, node)
            treepids[task] = pid

        notask = 0
        for sid in sapnotes:
            #~ Get category
            compkey = escape(sapnotes[sid]['componentkey'])
            catname = escape(sapnotes[sid]['category'])


            #~ Get tasks for this sapnote
            try:
                tasks = sapnotes[sid]['tasks']
            except:
                sapnotes[sid]['tasks'] = tasks = []


            if len(tasks) == 0:
                # Components in no-task node
                cmpkey = "notask" + '-' + compkey
                comptxt = dcomp[compkey]
                try:
                    pid = treepids[cmpkey]
                except:
                    node = self.get_node_component(compkey, comptxt)
                    pid = self.model.append(treepids['None'], node)
                    treepids[cmpkey] = pid

                # Categories in no-task node
                catkey = "notask" + '-' + compkey + '-' + catname
                try:
                    cid = treepids[catkey]
                except:
                    node = self.get_node_category(sapnotes[sid])
                    cid = self.model.append(pid, node)
                    treepids[catkey] = cid

                #~ SAP Note not linked to any task
                sapnote = self.get_node_sapnote(sapnotes[sid], sid)
                self.model.append(cid, sapnote)
                notask += 1
            else:
                #~ SAP Note linked to tasks
                for task in sapnotes[sid]['tasks']:
                    # Components in task node
                    cmpkey = task + '-' + compkey
                    comptxt = dcomp[compkey]
                    try:
                        pid = treepids[cmpkey]
                    except:
                        node = self.get_node_component(compkey, comptxt)
                        pid = self.model.append(treepids[task], node)
                        treepids[cmpkey] = pid

                    catkey = task + '-' + compkey + '-' + catname
                    try:
                        cid = treepids[catkey]
                    except:
                        node = self.get_node_category(sapnotes[sid])
                        cid = self.model.append(pid, node)
                        treepids[catkey] = cid

                    pid = treepids[task]
                    sapnote = self.get_node_sapnote(sapnotes[sid], sid)
                    self.model.append(cid, sapnote)

        #~ "No task assigned" node deletion if no tasks at all
        if notask == 0:
            self.model.remove(treepids['None'])


    def get_node_component(self, compkey, comptxt):
        #~ compkey = escape(sapnote['componentkey'])
        #~ comptxt = escape(sapnote['componenttxt'])
        icon = self.im.get_icon('component')
        node = []
        component = "<big><b>%s</b></big> (<i>%s</i>)" % (compkey, comptxt) # component
        #~ component = "<big><b>%s</b></big>" % (compkey)
        #~ component = "<span size='18000'><b>%s</b></span> <span size='12000'>(<i>%s</i>)</span>" % (compkey, comptxt)
        node.append('component')
        node.append(0)
        node.append(icon)
        node.append(component) # Component
        node.append("") # Category
        node.append("") # Type
        node.append(compkey) # Id
        node.append("") # Title
        node.append("") # Priority
        node.append("") # Lang
        #~ node.append("") # Version
        node.append("") # Release on
        return node


    def get_node_category(self, sapnote):
        compkey = escape(sapnote['componentkey'])
        catname = escape(sapnote['category'])
        catkey = compkey + '-' + catname
        icon = self.im.get_icon('category')

        if len(catname) == 0:
            #~ catname = "<span size='12000'><b>No category assigned</b></span>"
            catname = "\t<big><b>No category assigned</b></big>"
        else:
            #~ category = "<span size='15000'><b>%s</b></span>" % catname
            category = "\t<big><b>%s</b></big>" % catname

        node = []
        node.append('category')
        node.append(0)
        node.append(icon)
        node.append(category) # Component
        node.append("") # Category
        node.append("") # Type
        node.append("") # Id
        node.append("") # Title
        node.append("") # Priority
        node.append("") # Lang
        #~ node.append("") # Version
        node.append("") # Release on
        return node


    def get_node_sapnote(self, sapnote, sid):
        compkey = escape(sapnote['componentkey'])
        icon_note = self.im.get_pixbuf_icon('sapnote')
        icon_fav = self.im.get_icon('bookmark')
        compkey = escape(sapnote['componentkey'])
        compkey = escape(sapnote['componentkey'])
        catname = escape(sapnote['category'])
        sn = "%10d" % (int(sid)) # SAP Note Id (000000nnnn)

        # Get bookmark
        try:
            bookmark = sapnote['bookmark']
        except Exception as error:
            bookmark = False

        # Get correct title
        if self.get_view() == 'bookmarks':
            title = "<big>%s</big>" % (escape(sapnote['title']))
        elif self.get_view() == 'components':
            title = "\t\t<big>SAP Note <b>%s</b> - %s</big>" % (sn, escape(sapnote['title']))
        else:
            title = "\t\t<big><b>SAP Note %s</b> - %s</big>" % (sn, escape(sapnote['title']))

        node = []
        # 0. # RowType
        node.append('sapnote')

        # 1. # CheckBox
        node.append(0)

        # 2. # Icon
        if bookmark:
            node.append(icon_fav)
        else:
            node.append(icon_note)
            #~ node.append(None)

        # 3. # Component
        if self.view == 'components':
            node.append(title)
            # 4. # Category
            node.append("")
        elif self.view == 'bookmarks':
            node.append("<big>%s</big>" % compkey)
            # 4. # Category
            node.append("%s" % catname)
            #~ node.append(catname)
        else:
            node.append(title)
            # 4. # Category
            node.append("")

        # 5. # Type
        node.append(sapnote['type'])

        # 6. # Sap Note ID
        node.append("%s" %sid)

        # 7. # Title
        if self.view == 'bookmarks':
            node.append(title)
        else:
            node.append("")

        # 8. # Priority
        priority = "%s" % escape(sapnote['priority'])
        node.append(priority)

        # 9. # Lang
        node.append(sapnote['language'])

        # 10. # Release date
        released = dateparser.parse(sapnote['releaseon'])
        node.append(released.strftime("%Y.%m.%d"))

        return node


    def populate_by_components(self, sapnotes, only_bookmarks=False):
        #~ self.log.debug('Populating by components')
        self.model.clear()
        self.treepids = {}
        self.column_component.set_title('Components')
        self.column_sid.set_visible(False)
        self.column_title.set_visible(False)
        self.set_headers_visible(False)
        self.set_grid_lines(Gtk.TreeViewGridLines.VERTICAL)

        self.column_title

        if len(sapnotes) == 0:
            return

        scomp = set()
        dcomp = {}

        for sid in sapnotes:
            compkey = escape(sapnotes[sid]['componentkey'])
            comptxt = escape(sapnotes[sid]['componenttxt'])
            scomp.add(compkey)
            dcomp[compkey] = comptxt
        lcomp = list(scomp)
        lcomp.sort()

        for compkey in lcomp:
            node = self.get_node_component(compkey, dcomp[compkey])
            pid = self.model.append(None, node)
            self.treepids[compkey] = pid

        for sid in sapnotes:
            #~ Gety component
            compkey = escape(sapnotes[sid]['componentkey'])
            #~ try:
            pid = self.treepids[compkey]
            #~ except:
                #~ node = self.get_node_component(sapnotes[sid])
                #~ pid = self.model.append(None, node)
                #~ self.treepids[compkey] = pid

            #~ Get category
            catname = escape(sapnotes[sid]['category'])
            catkey = compkey + '-' + catname
            try:
                cid = self.treepids[catkey]
            except:
                node = self.get_node_category(sapnotes[sid])
                cid = self.model.append(pid, node)
                self.treepids[catkey] = cid

            #~ Get SAP Note
            if only_bookmarks:
                try:
                    bookmark = sapnotes[sid]['bookmark'] # True or False
                except:
                    bookmark = False
                if bookmark:
                    node = self.get_node_sapnote(sapnotes[sid], sid)
                    self.model.append(cid, node)
            else:
                node = self.get_node_sapnote(sapnotes[sid], sid)
                self.model.append(cid, node)


    def changed(self, *args):
        try:
            model, treeiters = self.selection.get_selected_rows()
            selected = set()
            if len(treeiters) > 0:
                for treeiter in treeiters:
                    if treeiter != None:
                        selected.add(model[treeiter][0])
        except Exception as error:
            self.log.error (self.get_traceback())


    def on_cell_toggled(self, widget, path):
        model = self.get_model()
        rtype = model[path][0]
        if rtype != 'component' and rtype != 'category':
            model[path][1] = not model[path][1]
            self.count = 0
            self.check_states()


    def check_states(self):
        lblSelectedNotes = self.gui.get_widget('lblSelectedNotes')
        self.selected = set()

        def traverse_treeview(model, path, iter, user_data=None):
            rtype = model.get_value(iter, 0)
            if rtype == 'component':
                # select everything (categories and notes)
                component = rtype = model.get_value(iter, 3)
                ce = component.find('</b></big>')
                compkey = component[8:ce]
            elif rtype == 'category':
                # select all notes under that category
                category = rtype = model.get_value(iter, 3)
                ce = category.find("</b></big>")
                catkey = category[9:ce]

            toggled = model.get_value(iter, 1)
            if toggled:
                self.count += 1
                title = model.get_value(iter, 3)
                sapnote = model.get_value(iter, 6)
                self.selected.add(sapnote)
            return False

        model = self.get_model()
        model.foreach(traverse_treeview)
        lblSelectedNotes.set_markup('<big>%d of %d\nSAP Notes selected</big>' % (len(self.selected), self.sap.get_total()))
        actions = self.gui.get_widget('mnuBtnActions')
        if (len(self.selected)) > 0:
            actions.set_sensitive(True)
            self.cb.setup_menu_actions()
        else:
            actions.set_sensitive(False)


    def set_select_notes(self, sapnotes):
        self.selected = set()
        for sapnote in sapnotes:
            self.selected.add(sapnote)


    def get_selected_notes(self):
        return self.selected


    def get_view(self):
        if self.view is None:
            return 'components'

        return self.view


    def set_view(self, view):
        settings = self.app.get_service('Settings')

        if view is None:
            view = settings.get_config_value('View')

        # Save view to settings
        if view not in ['settings', 'download']:
            self.view = view
            settings = self.app.get_service('Settings')
            settings.set_config_value('View', view)

        # Change icon
        iconview = self.gui.get_widget('imgViewCurrent')
        if view == 'settings':
            iconname = 'gtk-preferences'
        elif view == 'download':
            iconname = 'download'
        else:
            iconname = view

        icon = self.im.get_pixbuf_icon(iconname, 48, 48)
        iconview.set_from_pixbuf(icon)

        # Change label
        viewlabel = self.gui.get_widget('lblViewCurrent')
        name = "<span size='20000'><b>%-10s</b></span>" % view.capitalize()
        viewlabel.set_markup(name)



    def expand(self):
        switch = self.gui.get_widget('schExpandCollapse')
        switch.set_active(True)

    def collapse(self):
        switch = self.gui.get_widget('schExpandCollapse')
        switch.set_active(False)

    def expand_collapse(self, switch, active):
        if active:
            self.expand_all()
        else:
            self.collapse_all()


    def select_all_none(self, switch, active):
        model = self.get_model()

        def traverse_treeview(model, path, iter, user_data=None):
            rtype = model.get_value(iter, 0)
            if rtype == 'sapnote':
                model.set_value(iter, 1, active)

            return False

        model.foreach(traverse_treeview, active)
        self.check_states()


    def select_by_component(self, component_target, active):
        model = self.get_model()

        def traverse_treeview(model, path, iter, user_data=None):
            rtype = model.get_value(iter, 0)
            if rtype == 'sapnote':
                sid = model.get_value(iter, 6)
                sapnote = self.sap.get_node(sid)
                component_source = sapnote['componentkey']
                #~ self.log.debug ("%s - %s" % (component_source, component_target))
                #~ if component_source.startswith(component_target):
                if component_source == component_target:
                    model.set_value(iter, 1, active)

            return False

        model.foreach(traverse_treeview, True)
        self.check_states()


    def select_by_task(self, task_target, active):
        model = self.get_model()

        def traverse_treeview(model, path, iter, user_data=None):
            rtype = model.get_value(iter, 0)
            if rtype == 'sapnote':
                sid = model.get_value(iter, 6)
                sapnote = self.sap.get_node(sid)
                tasks_source = sapnote['tasks']

                if task_target in tasks_source:
                    model.set_value(iter, 1, active)
                else:
                    if len(task_target) == 0 and len(tasks_source) == 0:
                        model.set_value(iter, 1, active)

            return False

        model.foreach(traverse_treeview, True)
        self.check_states()
