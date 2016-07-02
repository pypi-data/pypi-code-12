

from .Importer.QtGui import *

from .SpellingLineEdit import SpellingLineEdit
from .LinkTextBrowser import LinkTextBrowser
from .Debug import debug
from .Find import Find
from .AutoScroll import AutoScroll

class MessageTab(QWidget):
    """A tab for holding a private message conversation.

    Allows private conversations to be split off from the main window IRC-style
    for neatness and reduction of accidental public messages."""
    def __init__(self, room_name, users, room_tab, cmdstr, *args, **kwargs):
        debug.debug("Creating MessageTab")
        QWidget.__init__(self, *args, **kwargs)

        self.room_name = room_name
        self.users = users
        self.room_tab = room_tab
        self.server = room_tab.server
        self.id = cmdstr

        self.all_available = True
        self.shown = True

        self.do_layout()
        self.set_users()

    def do_layout(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.header = QLabel()
        self.header.setWordWrap(True)
        layout.addWidget(self.header)

        self.msg_stream = LinkTextBrowser(self.room_tab.server)
        layout.addWidget(self.msg_stream)
        self.msg_stream.setOpenExternalLinks(True)
        self.msg_stream.setOpenLinks(False)
        self.msg_stream.setSearchPaths([QApplication.instance().cache_dir.path()])
        self.msg_stream.anchorClicked.connect(self.handle_URL)

        self.msg_stream.timestamp_action = self.room_tab.timestamp_action
        self.addAction(self.room_tab.timestamp_action)

        self.find = Find(self.msg_stream)
        layout.addWidget(self.find)

        self.input_box = SpellingLineEdit(self.room_tab.msg_target.sizeHint().height() + 2)
        layout.addWidget(self.input_box)
        self.input_box.returnPressed.connect(self.send_msg)

    def set_users(self):
        userstr = ", ".join(self.users)
        self.header.setText("Private message in {} with {}".format(self.room_name, userstr))
        # truncate long lists of names
        self.name = userstr[:30]

    def add_msg(self, msg):
        #TODO maybe de-green and reformat to regular messages
        with AutoScroll(self.msg_stream) as scroll:
            scroll.insert(msg)

    def send_msg(self):
        msg = self.input_box.text()
        self.input_box.setText("")
        if not msg:
            return
        if msg.startswith("/me "):
            # reformat /mes to keep in green to avoid accidental escapes
            msg = "*" + msg[4:] + "*"
        if msg[0] == "/":
            self.room_tab.parse_cmd(msg)
        else:
            if not self.all_available:
                item = list(self.users)[0]
                if (len(self.users) == 1) & ((item.endswith("Bot")) | (item == "Bots")):
                    # this is probably a bot and needs to be addressed with /b
                    # this detection is not perfect, and will cause issues with trying
                    # to /msg a user with a name ending in "Bot" who is currently
                    # offline, but it should work otherwise
                    msg = "/b " + msg
                else:
                    QMessageBox.warning(self, "User not online", "Not all users in this conversation are currently online. You cannot send messages to them.")
                    return
            else:
                msg = "/msg " + ", ".join(self.users) + " " + msg
            self.room_tab.post_msg(msg)

    def leave(self):
        self.close_tab()

    def close_tab(self):
        debug.debug("Closing tab")
        self.parent().parent().removeTab(self.parent().parent().indexOf(self))
        self.shown = False

    def handle_URL(self, url):
        self.room_tab.server.handle_URL(url)
        self.input_box.setFocus()

    def reload_stream(self):
        self.room_tab.reload_stream()

    def show_find(self):
        self.find.toggle_visible()

    def users_online(self, users):
        for i in self.users:
            if i not in users:
                self.all_available = False
                break
        else:
            self.all_available = True
        self.color_input_box()

    def color_input_box(self, text=None):
        if self.room_tab.away_remind and self.room_tab.away:
            self.input_box.setStyleSheet("""QPlainTextEdit {
                border: 3px solid purple;
                border-radius: 3px;
            }""")
        else:
            self.input_box.setStyleSheet("")
