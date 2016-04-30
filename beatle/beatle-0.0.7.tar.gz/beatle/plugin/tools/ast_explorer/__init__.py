# -*- coding: utf-8 -*-
import wx
from  ctx import theContext as context
import analytic.astd as astd
import model.file
from ToolAstExplorerPane import ToolAstExplorerPane
import app.resources as rc


class ast_explorer(wx.PyEvtHandler):
    """Class for providing ast explorer"""
    instance = None

    def __init__(self):
        """Initialize ast explorer"""
        super(ast_explorer, self).__init__()
        #create the menus
        self._menuid = context.frame.new_tool_id()
        self._imenu = wx.MenuItem(context.frame.menuTools, self._menuid, u"Ast explorer",
            u"show ast structure", wx.ITEM_NORMAL)
        context.frame.AddToolsMenu('Ast explorer', self._imenu)
        #bind the menu handlers
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateAstExplorer, id=self._menuid)
        self.Bind(wx.EVT_MENU, self.OnAstExplorer, id=self._menuid)

    @classmethod
    def load(cls):
        """Setup tool for the environment"""
        return ast_explorer()

    def OnUpdateAstExplorer(self, event):
        """Handle the update"""
        # get the view book
        self.selected = None
        book = context.frame.viewBook
        try:
            view = book.GetCurrentPage()
            if view is not None:
                # get the selected item
                selected = view.selected
                if type(selected) is model.file.File:
                    if selected.project._language == 'python':
                        self.selected = selected
        except:
            pass
        event.Enable(bool(self.selected))

    def OnAstExplorer(self, event):
        """Handle the command"""
        item = self.selected
        path = item.abs_file
        try:
            with open(path, "r") as python_file:
                content = python_file.read()
                data = astd.parse(content)
        except:
            wx.MessageBox("The file contains errors", "Error",
                wx.OK | wx.CENTER | wx.ICON_ERROR, context.frame)
            return
        frame = context.frame
        p = ToolAstExplorerPane(frame.docBook, item, data)
        frame.docBook.Freeze()
        frame.docBook.AddPage(p, path, True, rc.GetBitmapIndex("mini_logo"))
        frame.docBook.Thaw()

