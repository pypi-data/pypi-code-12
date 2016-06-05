# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import wx
from  ctx import theContext as context
import analytic.astd as astd
import model.file
from WebBrowserPane import WebBrowserPane
import app.resources as rc


class web_browser(wx.PyEvtHandler):
    """Class for providing ast explorer"""
    instance = None

    def __init__(self):
        """Initialize web explorer"""
        super(web_browser, self).__init__()
        #create the menus
        self._menuid = context.frame.new_tool_id()
        self._imenu = wx.MenuItem(context.frame.menuTools, self._menuid, u"Web browser",
            u"show embedded web browser", wx.ITEM_NORMAL)
        context.frame.AddToolsMenu('Web browser', self._imenu)
        #bind the menu handlers
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateWebBrowser, id=self._menuid)
        self.Bind(wx.EVT_MENU, self.OnWebBrowser, id=self._menuid)

    @classmethod
    def load(cls):
        """Setup tool for the environment"""
        return web_browser()

    def OnUpdateWebBrowser(self, event):
        """Handle the update"""
        event.Enable(True)

    def OnWebBrowser(self, event):
        """Handle the command"""
        frame = context.frame
        p = WebBrowserPane(frame.docBook, frame)
        frame.docBook.Freeze()
        frame.docBook.AddPage(p, 'web', True, rc.GetBitmapIndex("info"))
        p.NavigateTo('https://www.google.com/')
        frame.docBook.Thaw()
