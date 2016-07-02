from collections import defaultdict
from urllib.parse import urlencode
import os

from lxml import html
from .Importer.QtCore import *
from .Importer.QtGui import *
from .Importer.QtNetwork import *

from .ChatTab import ChatTab, EncodingManager
from .WebTab import WebTab
from .SettingsConvenience import settings_get_bool
from .Debug import debug
from .FormRequest import FormRequest

class Server(QObject):
    def __init__(self, dialog_parent, *args, **kwargs):
        QObject.__init__(self, *args, **kwargs)
        self.dialog_parent = dialog_parent
        self.img_popups = {}
        debug.debug("Server created")
        self.valid = False

        args = self.parent().args
        # the server to connect to can only be set on the command line for now
        # this should be available as a combobox/etc later
        if args["server"] is not None:
            server = args["server"]
            if not server.startswith("http://"):
                server = "http://" + server
            server = QUrl(server)
            self.domain = server.host()
            path = server.path()
            if path.endswith("index.cgi"):
                path = path[:-len("index.cgi")]
            if not path.endswith("/"):
                path += "/"
            self.path = path
            if server.port() != -1:
                self.port = ":" + str(server.port())
            else:
                self.port = ""
        else:
            self.domain = ""
            self.path = ""
            self.port = ""
        if (not self.domain) | (not self.path):
            self.domain = "www.rinkworks.com"
            self.path = "/rinkchat/"
            self.port = ""
        self.url = QUrl("http://" + self.domain + self.port + self.path + "index.cgi")
        self.server_name = args["server_name"] if args["server_name"] is not None else "RinkChat"
        self.dialog_parent.setWindowTitle("{} - PyRook".format(self.server_name))
        args_username = args["username"] if args["username"] is not None else ""
        args_password = args["password"] if args["password"] is not None else ""
        settings = QSettings()
        sett_username = settings.value("account/username", "")
        sett_password = settings.value("account/password", "")
        self.username = args_username or sett_username
        self.password = args_password or sett_password

        # this is the manager that handles all non-stream requests for the server
        # chatstreams must be handled separately as the manager has a limit on
        # concurrent requests, so each tab creates its own manager to handle just the
        # chatstream
        self.manager = EncodingManager(self)
        debug.debug("Network manager created")

        self.settings_changed()
        self.parent().settings_changed.connect(self.settings_changed)

        if (self.username != "") & (self.password != ""):
            # we have a username and password, remembered or supplied as args
            # skip dialogue box requesting them
            # (note: if the username and password are incorrect, it will correctly ask instead)
            if sett_username and not args_username:
                # we got the username and password from memory, not cmd line args
                self.remember_username = True
                self.remember_password = True
            else:
                self.remember_username = False
                self.remember_password = False
            self.log_in()
        else:
            self.create_server()

    def create_server(self):
        # pop up QDialog to get information on a server
        server_dialog = QDialog(self.dialog_parent)
        server_dialog.setWindowTitle("Login - PyRook")
        debug.debug("Server dialog created")
        server_dialog.setAttribute(Qt.WA_DeleteOnClose)
        # set up dialog
        server_layout = QFormLayout(server_dialog)

        # create text fields
        username_line_edit = QLineEdit()
        username_line_edit.setText(self.username)
        username_line_edit.textEdited.connect(self.setUsername)
        server_layout.addRow("&Username:", username_line_edit)

        password_line_edit = QLineEdit()
        password_line_edit.setEchoMode(QLineEdit.Password)
        password_line_edit.setText(self.password)
        password_line_edit.textEdited.connect(self.setPassword)
        server_layout.addRow("&Password:", password_line_edit)

        settings = QSettings()
        remember_username_box = QCheckBox()
        remember_username_box.setChecked(True if settings.value("account/username", "") else False)
        remember_username_box.toggled.connect(self.set_remember_username)
        self.remember_username = remember_username_box.isChecked()
        server_layout.addRow("Remember username:", remember_username_box)

        remember_password_box = QCheckBox()
        remember_password_box.setChecked(True if settings.value("account/password", "") else False)
        remember_password_box.toggled.connect(self.set_remember_password)
        self.remember_password = remember_password_box.isChecked()
        server_layout.addRow("Remember password:", remember_password_box)

        # create buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Cancel)
        connect_button = QPushButton(QIcon.fromTheme("dialog-ok"), "Connect")
        button_box.addButton(connect_button, QDialogButtonBox.AcceptRole)
        button_box.accepted.connect(server_dialog.accept)
        button_box.rejected.connect(server_dialog.reject)

        server_layout.addRow(button_box)

        # make dialog modal
        debug.debug("Displaying server dialog")
        server_dialog.setWindowModality(Qt.WindowModal)
        if server_dialog.exec_():
            self.log_in()

    def log_in(self):
        debug.debug("Requesting login...")
        self.login = self.manager.post(FormRequest(self.url), urlencode({
            "action":"login",
            "name":self.username,
            "pass":self.password}))
        self.login.error.connect(self.login_failed)
        self.login.finished.connect(self.logged_in)

    def setUsername(self, username):
        self.username = username

    def setPassword(self, password):
        self.password = password

    def set_remember_username(self, state):
        self.remember_username = state

    def set_remember_password(self, state):
        self.remember_password = state

    def logged_in(self):
        debug.debug("Login replied")
        # first check an error hasn't also happened
        if self.login.error() != QNetworkReply.NoError:
            return

        # retrieve login page
        # handle parsing with non-Qt elements 'cos I couldn't get Qt to behave
        response = html.document_fromstring(str(self.login.readAll()))
        self.login.deleteLater()

        # I seem to be getting empty responses which cause parsing to fail; catch that case
        # and behave as in login failure
        if response == None:
            debug.debug("Empty response to login request.")
            self.login_failed()

        error = []
        for i in response.xpath("descendant-or-self::body/descendant-or-self::*/div[@id = 'content']/descendant-or-self::*/font[@color = 'red']"):
            error.append(i.text_content())

        if error:
            debug.debug("Login failed")
            fail = QMessageBox.warning(self.dialog_parent, error[0], error[1])
            self.create_server()
        else:
            debug.debug("Login successful!")
            # store username/password if desired
            settings = QSettings()
            if self.remember_username:
                settings.setValue("account/username", self.username)
            if self.remember_password:
                settings.setValue("account/password", self.password)
            # create a room tab
            self.valid = True
            room = ChatTab(self, parent=self.dialog_parent)
            self.dialog_parent.tabwidget.addTab(room, room.name)

    def login_failed(self):
        debug.debug("Login error")
        # handle login network errors
        # for now this is just a generic oops
        self.login.deleteLater()
        ret = QMessageBox.warning(self.dialog_parent, "Network Error", "There was a network error logging in. Retry?", QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.create_server()
        else:
            self.parent().server = None

    def handle_URL(self, url, page=None):
        # handler for clicked URLS
        if url.scheme() == "img":
            # this is an internal image expansion url
            path = url.path()
            if os.path.exists(path):
                popup = CleaningLabel(self.img_popups, path)
                popup.setPixmap(QPixmap(path))
                popup.setWindowTitle("PyRook - Expanded bot image")
                popup.show()
                self.img_popups[path] = popup
                self.dialog_parent.destroyed.connect(popup.close)
            return

        url, external = self.parse_URL(url)
        if external:
            QDesktopServices.openUrl(url)
        else:
            action = self.get_URL_query_item(url, "action")
            if action == "enter":
                # room join request, intercept
                room = ChatTab(self, room={"id":self.get_URL_query_item(url, "room"), "name":"Loading..."}, parent=self.dialog_parent)
                self.dialog_parent.tabwidget.addTab(room, room.name)
                return
            if (WebTab is not None) & (self.web_tabs):
                # we have embedded WebKit, so open the page internally
                if page is None:
                    page = WebTab(self)
                    self.dialog_parent.tabwidget.addTab(page, page.title() or "Loading...")
                    page.titleChanged.connect(page.set_title)
                page.load(url)
            else:
                QDesktopServices.openUrl(url)

    def parse_URL(self, url):
        target = self.get_URL_query_item(url, "url")
        if target:
            return QUrl(target), True
        # check if the url actually points at our server
        host = url.host()
        if host:
            if host != self.domain:
                return url, True
        # this is an internal URL
        # deal with inconsistent relative/absolute pathing from different sources
        try:
            query = bytes(url.encodedQuery()).decode("ascii")
        except AttributeError:
            query = url.query(QUrl.FullyEncoded)
        if url.path().startswith(self.path):
            url = QUrl("http://" + self.domain + url.path() + "?" + query)
        else:
            url = QUrl("http://" + self.domain + self.path + url.path() + "?" + query)
        return url, False

    def get_URL_query_item(self, url, key):
        try:
            return url.queryItemValue(key)
        except AttributeError:
            return QUrlQuery(url).queryItemValue(key, QUrl.FullyDecoded)

    def handle_URL_action(self, action):
        url = "index.cgi?action=" + action
        if self.username:
            url += "&name=" + self.username
        if (self.password != "") & (action in ("options", "profile", "account", "memos", "memolists")):
            url += "&pass=" + self.password
        self.handle_URL(QUrl(url))

    def settings_changed(self):
        self.web_tabs = settings_get_bool("config/web_tabs", True)


class CleaningLabel(QLabel):
    """A QLabel which deletes references to itself when it closes."""
    def __init__(self, store, name, *args):
        QLabel.__init__(self, *args)
        self.store = store
        self.name = name

    def closeEvent(self, e):
        del self.store[self.name]
        QLabel.closeEvent(self, e)
