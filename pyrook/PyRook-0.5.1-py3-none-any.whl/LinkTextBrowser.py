

from .Importer.QtCore import *
from .Importer.QtGui import *

from .Debug import debug

class LinkTextBrowser(QTextBrowser):
    """A QTextBrowser which overrides the default context menu to adjust link locations."""
    def __init__(self, server, *args, **kwargs):
        self.server = server
        QTextBrowser.__init__(self, *args, **kwargs)
        self.timestamp_action = None

    def contextMenuEvent(self, event):
        self.link_pos = event.pos()
        self.link_pos.setX(self.link_pos.x() + self.horizontalScrollBar().value())
        self.link_pos.setY(self.link_pos.y() + self.verticalScrollBar().value())
        menu = self.createStandardContextMenu(self.link_pos)

        # add timestamp toggle action
        if self.timestamp_action:
            menu.addSeparator()
            menu.addAction(self.timestamp_action)

        # this *should* always be a copy link location item, but I am NOT totally sure
        # this is consistent
        link_location = menu.actions()[1]
        # it doesn't appear to be possible to do
        # link_location.disconnect(SIGNAL("triggered()"), self, SLOT("_q_copyLink()"))
        # claims "No such slot LinkTextBrowser::_q_copyLink()"
        # so do a general disconnect and hope this is the right action
        link_location.triggered.disconnect()
        link_location.triggered.connect(self.copy_link)
        self.link_pos = event.pos()

        menu.popup(event.globalPos())
        # ensure menu doesn't get garbage collected before display
        self.menu = menu

    def copy_link(self):
        link_text = self.anchorAt(self.link_pos)
        url, external = self.server.parse_URL(QUrl(link_text))
        c = QApplication.clipboard()
        u = url.toString()
        c.setText(u)
        if c.supportsSelection():
            c.setText(u, QClipboard.Selection)
