from PyQt5 import QtGui

from hackedit.api import system
from hackedit.api.widgets import PreferencePage
from hackedit.app import settings
from hackedit.app.forms import settings_page_behaviour_ui


class Behaviour(PreferencePage):
    """
    Preference page for the application behaviours settings
    """
    def __init__(self):
        super().__init__(_('Behaviour'),
                         icon=QtGui.QIcon.fromTheme('preferences-system'),
                         category=_('Environment'))
        self.ui = settings_page_behaviour_ui.Ui_Form()
        self.ui.setupUi(self)

    def reset(self):
        self.ui.cb_confirm_exit.setChecked(settings.confirm_app_exit())
        self.ui.cb_restore_session.setChecked(settings.restore_session())
        self.ui.cb_reopen.setChecked(settings.restore_last_window())
        self.ui.cb_splashscreen.setChecked(settings.show_splashscreen())
        self.ui.cb_check_for_updates.setChecked(
            settings.automatically_check_for_updates())
        mode = settings.open_mode()
        if mode == settings.OpenMode.NEW_WINDOW:
            self.ui.rb_open_proj_in_new.setChecked(True)
        elif mode == settings.OpenMode.CURRENT_WINDOW:
            self.ui.rb_open_proj_in_same.setChecked(True)
        else:
            self.ui.rb_open_proj_ask.setChecked(True)

    @staticmethod
    def restore_defaults():
        settings.set_show_splashscreen(True)
        settings.set_automatically_check_for_updates(
            False if system.LINUX else True)
        settings.set_open_mode(settings.OpenMode.ASK_EACH_TIME)
        settings.set_restore_last_window(False)
        settings.set_confirm_app_exit(True)
        settings.set_restore_session(True)

    def save(self):
        settings.set_show_splashscreen(self.ui.cb_splashscreen.isChecked())
        if self.ui.rb_open_proj_in_new.isChecked():
            settings.set_open_mode(settings.OpenMode.NEW_WINDOW)
        elif self.ui.rb_open_proj_in_same.isChecked():
            settings.set_open_mode(settings.OpenMode.CURRENT_WINDOW)
        else:
            settings.set_open_mode(settings.OpenMode.ASK_EACH_TIME)
        settings.set_restore_last_window(self.ui.cb_reopen.isChecked())
        settings.set_confirm_app_exit(self.ui.cb_confirm_exit.isChecked())
        settings.set_automatically_check_for_updates(
            self.ui.cb_check_for_updates.isChecked())
        settings.set_restore_session(self.ui.cb_restore_session.isChecked())
