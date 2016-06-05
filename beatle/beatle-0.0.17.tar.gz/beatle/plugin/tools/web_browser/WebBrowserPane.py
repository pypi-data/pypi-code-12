# -*- coding: utf-8 -*-

import app.ui.pane as pane


class WebBrowserPane(pane.NavigatorPane):
    """Implements web browser pane"""
    def __init__(self, parent, mainframe):
        """Intialization of method editor"""
        super(WebBrowserPane, self).__init__(parent, mainframe)
        self.m_url.Show(True)

    def OnEnterUrl(self, event):
        """Process enter text"""
        self._url = self.m_url.GetValue()
        self.m_page.LoadURL(self._url)


