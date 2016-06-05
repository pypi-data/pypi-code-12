# -*- coding: utf-8 -*-
import wx
import app
from  ctx import theContext as context


class AppSplashScreen(wx.SplashScreen):
    """
    Create a splash screen widget.
    """
    def __init__(self, parent=None):
        """Initialize splash screen"""
        aBitmap = wx.Image(name="app/res/beatle.jpg").ConvertToBitmap()
        splashStyle = wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT
        splashDuration = 2000  # milliseconds
        # Call the constructor with the above arguments in exactly the
        # following order.
        wx.SplashScreen.__init__(self, aBitmap, splashStyle,
                                 splashDuration, parent)
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        wx.YieldIfNeeded()

    def OnExit(self, evt):
        """Continue process"""
        self.Hide()
        app.mainWindow(self)
        context.frame.Show()
        wx.GetApp().SetTopWindow(context.frame)
        # The program will freeze without this line.
        evt.Skip()  # Make sure the default handler runs too...
