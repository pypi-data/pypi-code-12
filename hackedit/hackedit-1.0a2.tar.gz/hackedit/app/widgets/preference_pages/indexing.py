from PyQt5 import QtGui

from hackedit.app import settings
from hackedit.api import index, project
from hackedit.api.widgets import PreferencePage
from hackedit.app.forms import settings_page_indexing_ui


class Indexing(PreferencePage):
    """
    Preference page to configure indexing.
    """
    def __init__(self):
        if QtGui.QIcon.hasThemeIcon('database-index'):
            icon = QtGui.QIcon.fromTheme('database-index')
        else:
            icon = QtGui.QIcon.fromTheme('edit-find-replace')
        super().__init__('Indexing', icon=icon, category='Environment')
        self.ui = settings_page_indexing_ui.Ui_Form()
        self.ui.setupUi(self)
        self.ui.bt_rm.clicked.connect(self._rm_location)
        self.ui.bt_clear.clicked.connect(self._clear_db)

    def reset(self):
        self.ui.cb_enable_indexing.setChecked(settings.indexing_enabled())
        self.ui.list_projects.clear()
        paths = []
        for p in index.get_all_projects():
            paths.append(p.path)
        self.ui.list_projects.addItems(sorted(paths))

    @staticmethod
    def restore_defaults():
        settings.set_indexing_enabled(True)

    def save(self):
        enabled = self.ui.cb_enable_indexing.isChecked()
        if enabled and enabled != settings.indexing_enabled():
            self.app.flg_force_indexing = True
        settings.set_indexing_enabled(enabled)
        print(self.app.flg_force_indexing)

    def _rm_location(self):
        path = self.ui.list_projects.currentItem().text()
        try:
            project_files = project.get_projects()
        except AttributeError:
            pass
        else:
            self.app.flg_force_indexing = path in project_files
        index.remove_project(path)
        self.reset()

    def _clear_db(self):
        index.clear_database()
        self.reset()
        self.app.flg_force_indexing = True
