

from .Importer.QtGui import *



class AutoScroll(object):
    """A class to wrap events changing the field of view of a ScrollArea and
    automatically detect whether to scroll down.

    Also provides a convenience handler for inserting data into a TextEdit."""
    def __init__(self, scroll_area):
        self.scroll_area = scroll_area

    def __enter__(self):
        self.currentscroll = self.scroll_area.verticalScrollBar().value()
        self.currentmax = self.scroll_area.verticalScrollBar().maximum()
        return self

    def __exit__(self, e, v, t):
        if self.currentscroll < self.currentmax - 20:
            # margin for error here in case of being almost scrolled all the way down
            self.scroll_area.verticalScrollBar().setValue(self.currentscroll)
        else:
            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def insert(self, msg):
        cursor = self.scroll_area.textCursor()
        oldcursor = self.scroll_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.scroll_area.setTextCursor(cursor)
        self.scroll_area.insertHtml(msg)
        self.scroll_area.setTextCursor(oldcursor)
