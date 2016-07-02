import os
import platform
import re
import shutil

from .Importer.QtCore import *
from .Importer.QtGui import *

from .Debug import debug
from .ChatTab import ChatTab
from .Server import Server
from .SettingsDialog import SettingsDialog
from .SettingsConvenience import settings_get_bool
from . import __version__

class ChatWindow(QMainWindow):
    """A QMainWindow.

    Contains a list of tabs. Note that ChatWindow centralWidget is the tabWidget.
    Tabs are mostly ChatTabs, holding a chatroom, but may also be QtWebKit tabs
    or, conceivably, other widgets entirely."""
    def __init__(self, pyrook, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        debug.debug("MainWindow opened")
        self.pyrook = pyrook
        self.to_exit_count = -1

        settings = QSettings()
        geometry = settings.value("geometry0")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(500, 300)
        self.create_tab_widget()

        self.server = Server(self, parent=self.pyrook)
        self.pyrook.server = self.server
        self.create_menus()
        self.tabwidget.currentChanged.connect(self.tab_changed)
        self.pip_name = ""
        self.updating = False

        self.pyrook.settings_changed.connect(self.settings_changed)
        self.settings_changed()


    def create_menus(self):
        self.pyrook_menu = self.menuBar().addMenu("&PyRook")

        self.pyrook_menu.addAction(QIcon.fromTheme("tab-new"), "New Room", self.new_room, QKeySequence("Ctrl+T"))
        self.leave_action = self.pyrook_menu.addAction(QIcon.fromTheme("tab-close"), "Leave Room", self.close_tab, QKeySequence("Ctrl+W"))
        self.tab_changed(0)
        self.pyrook_menu.addAction(QIcon.fromTheme("view-refresh"), "Reload Stream", self.reload_stream, QKeySequence("F5"))
        self.pyrook_menu.addAction(QIcon.fromTheme("edit-find"), "Find", self.find, QKeySequence("Ctrl+F"))
        self.pyrook_menu.addAction("Focus input box", self.focus_input_box, QKeySequence("F4"))
        self.pyrook_menu.addSeparator()
        self.logdir_action = self.pyrook_menu.addAction("Open log folder", self.open_log_dir)
        self.logdir_action.setVisible(False)
        self.logdir_separator = self.pyrook_menu.addSeparator()
        self.logdir_separator.setVisible(False)
        self.pyrook_menu.addAction(QIcon.fromTheme("configure"), "Configure PyRook", self.settings_dialog)
        self.pyrook_menu.addAction("Update", self.update)
        self.pyrook_menu.addAction(QIcon.fromTheme("application-exit"), "Quit", self.pyrook.close_all, QKeySequence("Ctrl+Q"))

        self.server_menu = self.menuBar().addMenu("&{}".format(self.server.server_name))
        self.server_menu.addAction(URLAction("memos", self.server, "Memos", self))
        self.server_menu.addAction(URLAction("memolists", self.server, "Memo Lists", self))
        self.server_menu.addSeparator()
        self.server_menu.addAction(URLAction("options", self.server, "Options", self))
        self.server_menu.addAction(URLAction("profile", self.server, "Profile", self))
        self.server_menu.addAction(URLAction("account", self.server, "Account", self))

        self.help_menu = self.menuBar().addMenu("&Help")
        self.help_menu.addAction(URLAction("smileys", self.server, "Smileys", self))
        self.help_menu.addAction(URLAction("policy", self.server, "Policy", self))
        self.help_menu.addAction(URLAction("help", self.server, "Help", self))
        self.help_menu.addSeparator()
        self.help_menu.addAction("Show debug log", self.show_debug)
        self.help_menu.addAction("Show raw HTML", self.show_raw_html)
        self.help_menu.addSeparator()
        self.help_menu.addAction(QApplication.windowIcon(), "About PyRook", self.about_pyrook)
        self.help_menu.addAction(QIcon.fromTheme("help-about"), "About Qt", self.about_qt)

    def create_tab_widget(self):
        self.tabwidget = QTabWidget()
        self.setCentralWidget(self.tabwidget)
        self.tabwidget.setTabPosition(QTabWidget.South)
        self.tabwidget.setMovable(True)
        self.tabwidget.setTabsClosable(True)
        self.tabwidget.tabCloseRequested.connect(self.close_tab)
        self.tabwidget.currentChanged.connect(self.label_color)

        nexttab = QShortcut(QKeySequence("Ctrl+PgDown"), self)
        nexttab.activated.connect(self.tab_forward)
        prevtab = QShortcut(QKeySequence("Ctrl+PgUp"), self)
        prevtab.activated.connect(self.tab_backward)

        self.status_bar = QLabel()
        # set minimum height in order to vertically centre text
        # (widgets won't grow vertically as cornerWidgets)
        h = self.tabwidget.tabBar().size().height()
        self.status_bar.setMinimumHeight(h)
        self.tabwidget.setCornerWidget(self.status_bar, Qt.BottomRightCorner)

    def new_room(self):
        if self.tabwidget.currentIndex() == -1:
            if self.pyrook.server:
                if self.pyrook.server.valid:
                    room = ChatTab(self.pyrook.server, parent=self)
                    self.tabwidget.addTab(room, room.name)
                else:
                    self.pyrook.server.create_server()
            else:
                self.pyrook.server = Server(self, parent=self.pyrook)
        else:
            room = ChatTab(self.tabwidget.currentWidget().server, parent=self)
            self.tabwidget.addTab(room, room.name)

    def closeEvent(self, event):
        debug.debug("Received window close request, killing tabs")
        self.pyrook.quitting = True
        for i in list(self.server.img_popups.values()):
            i.close()
        while self.tabwidget.count():
            self.tabwidget.widget(0).leave()
        settings = QSettings()
        settings.setValue("geometry0", self.saveGeometry())
        event.accept()

    def close_tab(self, index=None):
        if index is None:
            self.tabwidget.currentWidget().leave()
        else:
            self.tabwidget.widget(index).leave()

    def tabRemoved(self):
        if self.tabwidget.count() == 0:
            room = ChatTab(self.server, parent=self)
            self.tabwidget.addTab(room, room.name)

    def tab_forward(self):
        self.tabwidget.setCurrentIndex((self.tabwidget.currentIndex() + 1) % self.tabwidget.count())

    def tab_backward(self):
        self.tabwidget.setCurrentIndex((self.tabwidget.currentIndex() - 1) % self.tabwidget.count())

    def tab_changed(self, index):
        if isinstance(self.tabwidget.currentWidget(), ChatTab):
            self.leave_action.setText("Leave Room")
        else:
            self.leave_action.setText("Close Tab")

    def reload_stream(self):
        self.tabwidget.currentWidget().reload_stream()

    def find(self):
        self.tabwidget.currentWidget().show_find()

    def settings_dialog(self):
        settings = SettingsDialog(self)
        settings.changed.connect(self.pyrook.settings_changed)
        settings.exec_()

    def show_debug(self):
        self.debug_console = QTextBrowser()
        self.debug_console.setLineWrapMode(QTextEdit.NoWrap)
        self.debug_console.setFontFamily("mono")
        self.debug_console.append("\n".join(debug.log))
        self.debug_console.setWindowTitle("Debug - PyRook")
        debug.updated.connect(self.debug_console.append)
        self.debug_console.show()

    def label_color(self, index):
        if not isinstance(index, int):
            # this seems to pass the actual tab, not the index, in some cases)
            index = self.tabwidget.indexOf(index)
        text = self.tabwidget.tabText(index)
        if text.startswith("*"):
            self.tabwidget.setTabText(index, text[1:-1])

    def about_pyrook(self):
        QMessageBox.about(self, "About PyRook", "PyRook " + __version__ + "\nA Python/Qt standalone client for RookChat.\nhttps://sentynel.com/project/PyRook\nBy Sam Lade")

    def about_qt(self):
        QMessageBox.aboutQt(self)

    def show_raw_html(self):
        w = self.tabwidget.currentWidget()
        if hasattr(w, "show_raw_html"):
            w.show_raw_html()

    def settings_changed(self):
        self.logging = settings_get_bool("config/logging")
        self.show_log_menu(self.logging)

    def show_log_menu(self, show):
        self.logdir_action.setVisible(show)
        self.logdir_separator.setVisible(show)

    def open_log_dir(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.join(self.pyrook.datadir, "logs")))

    def focus_input_box(self):
        w = self.tabwidget.currentWidget()
        if hasattr(w, "input_box"):
            w.input_box.setFocus()

    def update(self):
        if self.updating:
            return
        if self.pip_name is None:
            QMessageBox.warning(self, "Update error", "Could not update: pip doesn't seem to be available.")
            return
        elif not self.pip_name:
            p = shutil.which("pip3")
            if not p:
                p = shutil.which("pip")
            if not p:
                self.pip_name = None
                return self.update()
            self.pip_name = p
        self.updating = True
        self.status_bar.setText("Checking installation status ")
        self.update_proc = QProcess()
        self.update_proc.start(self.pip_name, ["list", "-l"])
        debug.debug("pip list -l")
        self.update_proc.finished.connect(self.update_listed)
        self.update_proc.error.connect(self.update_listed)

    def update_listed(self, code, status=None):
        res = bytes(self.update_proc.readAllStandardOutput() + self.update_proc.readAllStandardError()).decode("utf8")
        debug.debug(res)
        if code:
            QMessageBox.warning(self, "Update error", "Could not update: pip list failed: {}.".format(code))
            self.status_bar.setText(" ")
            self.updating = False
            return
        if "PyRook" not in res:
            QMessageBox.warning(self, "Update error", "Could not update: PyRook doesn't seem to be installed with pip.")
            self.status_bar.setText(" ")
            self.updating = False
            return
        self.update_proc = QProcess()
        self.update_proc.start(self.pip_name, ["show", "PyRook"])
        debug.debug("pip show PyRook")
        self.update_proc.finished.connect(self.update_shown)
        self.update_proc.error.connect(self.update_shown)

    def update_shown(self, code, status=None):
        res = bytes(self.update_proc.readAllStandardOutput() + self.update_proc.readAllStandardError()).decode("utf8")
        debug.debug(res)
        if code:
            QMessageBox.warning(self, "Update error", "Could not update: pip show failed: {}.".format(code))
            self.status_bar.setText(" ")
            self.updating = False
            return
        loc = re.search(r"Location: (.*)", res)
        if not loc:
            QMessageBox.warning(self, "Update error", "Could not update: Couldn't find PyRook install path.")
            self.status_bar.setText(" ")
            self.updating = False
            return
        self.update_proc = QProcess()
        self.status_bar.setText("Querying updates ")
        # other OSes may be out of luck here for the moment
        if platform.system() == "Linux" and not os.access(loc.group(1), os.W_OK):
            # need sudo
            self.update_proc.start("gksudo", ["-D", "PyRook auto update", " ".join((self.pip_name, "install", "--no-deps", "--upgrade", "PyRook"))])
            debug.debug("gksudo pip install PyRook")
        else:
            self.update_proc.start(self.pip_name, ["install", "--no-deps", "--upgrade", "PyRook"])
            debug.debug("pip install PyRook")
        self.update_proc.finished.connect(self.update_run)
        self.update_proc.error.connect(self.update_run)

    def update_run(self, code, status=None):
        res = bytes(self.update_proc.readAllStandardOutput() + self.update_proc.readAllStandardError()).decode("utf8")
        debug.debug(res)
        self.status_bar.setText(" ")
        self.updating = False
        if code:
            QMessageBox.warning(self, "Update error", "Could not update: pip install failed: {}.".format(code))
            return
        if "already up-to-date" in res:
            QMessageBox.information(self, "No update", "Update check finished, no updates available.")
        elif "Successfully installed PyRook" in res:
            QMessageBox.information(self, "Update installed", "Updated. Please restart PyRook.")
        else:
            QMessageBox.warning(self, "Update error", "Failed to parse update status output.")


class URLAction(QAction):
    url_triggered = Signal(str)
    def __init__(self, method, server, text, parent):
        QAction.__init__(self, text, parent)
        self.method = method
        self.triggered.connect(self.emit_url)
        self.url_triggered.connect(server.handle_URL_action)

    def emit_url(self):
        self.url_triggered.emit(self.method)
