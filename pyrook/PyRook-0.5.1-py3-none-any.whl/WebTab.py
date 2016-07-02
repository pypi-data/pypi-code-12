

from .Importer.QtGui import *
try: from .Importer.QtWebKit import *
except ImportError: WebKit = False
else: WebKit = True

from .Debug import debug

if WebKit:
    class WebTab(QWebView):
        """QWebView derived class which provides functions for PyRook's tab handling."""
        def __init__(self, server, *args, **kwargs):
            # this will be redundant if multiple WebTabs are created, but it
            # segfaults if it's done earlier (because QApplication doesn't exist)
            # and I don't want to duplicate the QtWebKit import logic
            settings = QWebSettings.globalSettings()
            settings.setFontFamily(QWebSettings.StandardFont, QFont().defaultFamily())
            QWebView.__init__(self, *args, **kwargs)
            self.name = "Loading..."
            self.server = server
            self.linkClicked.connect(self.handle_URL)
            self.urlChanged.connect(self.set_page_options)

            # add missing default shortcut for Windows
            copy = self.pageAction(QWebPage.Copy)
            copy.setShortcut(QKeySequence("Ctrl+C"))
            self.addAction(copy)

        def set_page_options(self):
            page = self.page()
            page.setLinkDelegationPolicy(QWebPage.DelegateAllLinks)

        def leave(self):
            self.close_tab()

        def close_tab(self):
            debug.debug("Closing tab")
            self.parent().parent().removeTab(self.parent().parent().indexOf(self))

        def set_title(self, title):
            self.parent().parent().setTabText(self.parent().parent().indexOf(self), title)
            self.name = title

        def handle_URL(self, url):
            self.server.handle_URL(url, self)

        def reload_stream(self):
            self.reload()

        def show_find(self):
            # unimplemented for the moment
            pass

else:
    WebTab = None
