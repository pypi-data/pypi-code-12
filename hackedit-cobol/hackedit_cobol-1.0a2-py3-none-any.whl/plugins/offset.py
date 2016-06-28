"""
Integrates the offset calculator view in a dock widget.
"""
from PyQt5 import QtCore, QtGui
from hackedit import api
from pyqode.cobol.widgets import PicOffsetsTable

from hackedit_cobol.plugins.editor import CobolEditor


class CobOffsetCalculator(api.plugins.WorkspacePlugin):
    """
    Integrates the offset calculator in the IDE as a dock widget.
    """
    def activate(self):
        self.table = PicOffsetsTable()
        self.dock = api.window.add_dock_widget(
            self.table, _('Offset calculator'),
            QtGui.QIcon.fromTheme('accessories-calculator'),
            QtCore.Qt.RightDockWidgetArea)
        self.dock.hide()
        api.signals.connect_slot(api.signals.EDITOR_CREATED,
                                 self._on_editor_created)

    def _on_editor_created(self, editor):
        if isinstance(editor, CobolEditor):
            mode = editor.modes.get('OffsetCalculatorMode')
            mode.pic_infos_available.connect(self._on_pic_info_available)

    def _on_pic_info_available(self, infos):
        self.table.update_pic_infos(infos)
        self.dock.show()
