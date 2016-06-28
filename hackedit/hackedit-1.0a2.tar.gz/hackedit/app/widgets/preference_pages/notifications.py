from PyQt5 import QtGui

from hackedit.api import events
from hackedit.app import settings
from hackedit.api.widgets import PreferencePage
from hackedit.app.forms import settings_page_notifications_ui


class Notifications(PreferencePage):
    """
    Preference page for the application notifications settings
    """
    def __init__(self):
        if QtGui.QIcon.hasThemeIcon('preferences-desktop-notification'):
            icon = QtGui.QIcon.fromTheme('preferences-desktop-notification')
        else:
            icon = QtGui.QIcon.fromTheme('dialog-information')
        super().__init__('Notifications', icon=icon, category='Environment')
        self.ui = settings_page_notifications_ui.Ui_Form()
        self.ui.setupUi(self)
        self.ui.blacklist.currentItemChanged.connect(self.update_buttons)
        self.ui.bt_rm.clicked.connect(self._rm_current_item_from_blacklist)
        self.ui.bt_clear.clicked.connect(self.ui.blacklist.clear)
        self.update_buttons()

    def _rm_current_item_from_blacklist(self):
        row = self.ui.blacklist.row(self.ui.blacklist.currentItem())
        self.ui.blacklist.takeItem(row)

    def update_buttons(self, *_):
        self.ui.bt_clear.setEnabled(self.ui.blacklist.count() > 0)
        self.ui.bt_rm.setEnabled(self.ui.blacklist.currentItem() is not None)

    def reset(self):
        self.ui.blacklist.clear()
        self.ui.cb_allow_system_tray.setChecked(
            settings.show_notification_in_sytem_tray())
        self.ui.cb_info.setChecked(settings.auto_open_info_notification())
        self.ui.cb_warning.setChecked(
            settings.auto_open_warning_notification())
        self.ui.cb_errors.setChecked(settings.auto_open_error_notification())
        self.ui.blacklist.addItems(events.get_blacklist())
        self.update_buttons()

    @staticmethod
    def restore_defaults():
        settings.set_show_notification_in_sytem_tray(True)
        settings.set_auto_open_info_notification(False)
        settings.set_auto_open_warning_notification(True)
        settings.set_auto_open_error_notification(True)
        events.clear_blacklist()

    def save(self):
        settings.set_show_notification_in_sytem_tray(
            self.ui.cb_allow_system_tray.isChecked())
        settings.set_auto_open_info_notification(self.ui.cb_info.isChecked())
        settings.set_auto_open_warning_notification(
            self.ui.cb_warning.isChecked())
        settings.set_auto_open_error_notification(
            self.ui.cb_errors.isChecked())
        events.set_blacklist([self.ui.blacklist.item(i).text()
                              for i in range(self.ui.blacklist.count())])
