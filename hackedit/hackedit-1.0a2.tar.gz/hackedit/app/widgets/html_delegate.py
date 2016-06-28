"""
This module contains a delegate used to render html text in abstract views.
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from hackedit.app.settings import dark_theme


class HTMLDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        style = QtGui.QApplication.style() if options.widget is None else \
            options.widget.style()

        doc = QtGui.QTextDocument()
        doc.setHtml(options.text)
        doc.setTextWidth(option.rect.width())
        doc.setDefaultStyleSheet(QtWidgets.qApp.styleSheet())

        if dark_theme():
            options.palette.setColor(QtGui.QPalette.Inactive,
                                     QtGui.QPalette.Highlight,
                                     QtCore.Qt.red)
            options.palette.setColor(QtGui.QPalette.Active,
                                     QtGui.QPalette.Highlight,
                                     QtCore.Qt.red)

        options.text = ""
        style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, options, painter,
                          options.widget)

        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()

        text_rect = style.subElementRect(QtWidgets.QStyle.SE_ItemViewItemText,
                                         options)
        painter.save()
        painter.translate(text_rect.topLeft())
        painter.setClipRect(text_rect.translated(-text_rect.topLeft()))

        is_dark = dark_theme()
        if option.state & QtWidgets.QStyle.State_Selected or is_dark:
            p = options.widget.palette()
            has_focus = option.state & QtWidgets.QStyle.State_HasFocus
            if has_focus:
                c = p.highlightedText().color()
            else:
                c = p.color(QtGui.QPalette.Inactive,
                            QtGui.QPalette.HighlightedText)
            if dark_theme():
                c = QtCore.Qt.white
            ctx.palette.setColor(QtGui.QPalette.Text, c)

        doc.documentLayout().draw(painter, ctx)

        painter.restore()

    def sizeHint(self, option, index):
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        doc = QtGui.QTextDocument()
        doc.setHtml(options.text)
        doc.setTextWidth(options.rect.width())
        h = doc.size().height()
        return QtCore.QSize(doc.idealWidth(), h)
