# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import os
import wx
from  ctx import theContext as context
import model.file
import app.resources as rc


class check_updates(wx.PyEvtHandler):
    """Class for providing check_updates"""
    instance = None

    def __init__(self):
        """Initialize ast explorer"""
        super(check_updates, self).__init__()
        #create the menus
        self._menuid = context.frame.new_tool_id()
        self._imenu = wx.MenuItem(context.frame.menuTools, self._menuid, u"Check updates",
            u"check for existing updates", wx.ITEM_NORMAL)
        context.frame.AddToolsMenu('Check updates', self._imenu)
        #bind the menu handlers
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateCheckUpdates, id=self._menuid)
        self.Bind(wx.EVT_MENU, self.OnCheckUpdates, id=self._menuid)

    @classmethod
    def load(cls):
        """Setup tool for the environment"""
        return check_updates()

    def OnUpdateCheckUpdates(self, event):
        """Handle the update"""
        event.Enable(True)

    def OnCheckUpdates(self, event):
        """Handle the command"""
        self.doUpdate()

    @staticmethod
    def parse_pkginfo(rawstring):
        """Parses pkginfo and returns a ddictionary"""
        lines = rawstring.splitlines(False)
        stripper = lambda x: (x[0].strip().upper(), x[1].strip())
        return dict([stripper(x.split(':', 1)) for x in lines if ':' in x])

    @staticmethod
    def pkginfo_version(pkg_dict):
        """Get comparable package info from dict"""
        return [int(ns) for ns in pkg_dict['VERSION'].split('.')]

    def doUpdate(self, automode=False):
        """Do the real update process"""
        # Check internet connection
        import socket
        try:
            socket.gethostbyname("pypi.python.org")
        except:
            if not automode:
                wx.MessageBox("Unable to access pypi repository.\nIs internect accesible?", "Error",
                    wx.OK | wx.CENTER | wx.ICON_ERROR, context.frame)
            return
        try:
            import urllib2
            raw = urllib2.urlopen('https://pypi.python.org/pypi?name=beatle&:action=display_pkginfo').read()
        except:
            if not automode:
                wx.MessageBox("We apologyze, but we can't access to beatle repository.\nPlease check again later.", "Error",
                    wx.OK | wx.CENTER | wx.ICON_ERROR, context.frame)
            return
        online_info = self.parse_pkginfo(raw)
        if 'VERSION' not in online_info:
            if not automode:
                wx.MessageBox("Missing version in beatle package", "Error",
                    wx.OK | wx.CENTER | wx.ICON_ERROR, context.frame)
            return
        try:
            import subprocess as sp
            raw, err = sp.Popen(['pip', 'show', 'beatle'], stdout=sp.PIPE, stderr=sp.PIPE).communicate()
        except:
            if not automode:
                wx.MessageBox("We apologyze, but we can't read beatle pip info.", "Error",
                    wx.OK | wx.CENTER | wx.ICON_ERROR, context.frame)
            return
        local_info = self.parse_pkginfo(raw)
        if 'VERSION' not in local_info:
            if not automode:
                wx.MessageBox("Missing version in beatle package", "Error",
                    wx.OK | wx.CENTER | wx.ICON_ERROR, context.frame)
            return
        online_version = self.pkginfo_version(online_info)
        local_version = self.pkginfo_version(local_info)
        if local_version >= online_version:
            if not automode:
                wx.MessageBox("Beatle is up to date!", "Info",
                    wx.OK | wx.CENTER | wx.ICON_INFORMATION, context.frame)
            return
        else:
            vo = local_info['VERSION']
            vn = online_info['VERSION']
            option = wx.MessageBox(
                "There are a new version of Beatle.\n"
                "your current version is {vo}\n"
                "the new version is {vn}\n"
                "Do you want to update?".format(vo=vo, vn=vn), "Info",
                    wx.YES_NO | wx.CENTER | wx.ICON_QUESTION, context.frame)
            if option != wx.YES:
                return
        # attempt to do without sudo
        success = True
        if os.system("pip install beatle --upgrade"):
            #Ok, now with sudo
            if os.system("gksudo 'pip install beatle --upgrade'"):
                success = False
        if success:
            wx.MessageBox(
                "Beatle is now up to date! Please restart the\n"
                "application for using the new version.", "Info",
                wx.OK | wx.CENTER | wx.ICON_INFORMATION, context.frame)
        else:
            wx.MessageBox("Beatle is not updated.", "Info",
                wx.OK | wx.CENTER | wx.ICON_INFORMATION, context.frame)

