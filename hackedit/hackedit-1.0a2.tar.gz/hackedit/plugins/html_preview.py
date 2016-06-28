"""
This module contains a plugin that is able to render the html preview of
the current editor.
"""
import logging
from PyQt5 import QtGui, QtCore
from pyqode.core.widgets import HtmlPreviewWidget

from hackedit import api


class HtmlPreview(api.plugins.WorkspacePlugin):
    def activate(self):
        self.preview = HtmlPreviewWidget()
        try:
            self.preview.set_editor(None)
        except AttributeError:
            self.preview.close()
            self.preview = None
            raise ImportError('failed to import QtWebKit or QtWebEngine')
        else:
            self._dock = api.window.add_dock_widget(
                self.preview, _('HTML Preview'), icon=QtGui.QIcon.fromTheme(
                    'text-html'), area=QtCore.Qt.RightDockWidgetArea)
            api.signals.connect_slot(api.signals.CURRENT_EDITOR_CHANGED,
                                     self.set_editor)
            self.preview.hide_requested.connect(self._dock.hide)
            self.preview.show_requested.connect(self._dock.show)
            self._dock.hide()

    def set_editor(self, editor):
        try:
            self.preview.set_editor(editor)
        except AttributeError:
            _logger().exception('failed to set editor on html preview')


def _logger():
    return logging.getLogger(__name__)
