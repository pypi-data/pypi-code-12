# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import wx
from  ctx import theContext as context
from ToolLogExplorerPane import ToolLogExplorerPane
import app.resources as rc


class log_explorer(wx.PyEvtHandler):
    """Class for providing log explorer"""
    instance = None

    def __init__(self):
        """Initialize log explorer"""
        super(log_explorer, self).__init__()
        #create the menus
        self._menuid = context.frame.new_tool_id()
        self._imenu = wx.MenuItem(context.frame.menuTools, self._menuid, u"Log explorer",
            u"show current transaction log", wx.ITEM_NORMAL)
        context.frame.AddToolsMenu('Log explorer', self._imenu)
        #bind the menu handlers
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateLogExplorer, id=self._menuid)
        self.Bind(wx.EVT_MENU, self.OnLogExplorer, id=self._menuid)

    @classmethod
    def load(cls):
        """Setup tool for the environment"""
        return log_explorer()

    def OnUpdateLogExplorer(self, event):
        """Handle the update"""
        event.Enable(True)

    def OnLogExplorer(self, event):
        """Handle the command"""
        # create a pane
        frame = context.frame
        p = ToolLogExplorerPane(frame.docBook)
        frame.docBook.AddPage(p, "Log explorer", True, rc.GetBitmapIndex("mini_logo"))

