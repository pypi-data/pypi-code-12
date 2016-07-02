import re
from urllib.parse import urlencode, parse_qs
from html import escape as html_escape
from time import time
import datetime
import os

from lxml import html
from lxml.html import builder
from lxml.etree import ParserError, XMLSyntaxError, Comment
from .Importer.QtCore import *
from .Importer.QtGui import *
from .Importer.QtNetwork import *

from .SettingsConvenience import settings_get_bool
from .Debug import debug
from .ThemeEngine import ThemeEngine, theme
from .LinkTextBrowser import LinkTextBrowser
from .SpellingLineEdit import SpellingLineEdit
from .Logger import Logger
from .MessageTab import MessageTab
from .Find import Find
from .AutoScroll import AutoScroll
from .FormRequest import FormRequest

class ChatTab(QWidget):
    """This container holds a single chatroom.

    It creates, displays and handles all widgets necessary to perform a room's functions,
    and is inserted into a ChatWindow's TabWidget"""
    raw_html_signal = Signal(str)
    purged_signal = Signal(str)
    def __init__(self, server, room=None, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        debug.debug("ChatTab created")
        # placeholder name until the actual name can be determined
        self.name = "Loading..."
        self.server = server
        self.quitting = False

        self.chatstream_request = None
        self.chatstream_timeout = None
        self.buff = ""
        self.kicked = False
        self.theme = None
        self.image_requests = []
        self.last_time = ""
        self.glow_color = None
        self.alert_wait = False
        self.alert_wait_timer = None
        self.away = False
        self.wrong_target = False
        self.inline_purging = False
        self.IP_re = re.compile(r"\[(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]")
        self.tsre = re.compile(r"\<\!\-\- \d{1,2}\/\d{1,2}\/\d{4}\, \d{2}\:\d{2}\:\d{2} \-\-\>")
        self.logger = None
        self.msgtab_list = {}
        self.chatstream_ts = 0
        self.last_data_timer = QTimer()
        self.last_data_timer.setInterval(1000*210) # chatstream keep-alives every 200s
        self.last_data_timer.timeout.connect(self.last_data_timeout)

        self.useful_html = []
        self.raw_html = []

        QApplication.instance().settings_changed.connect(self.settings_changed)
        self.settings_changed()

        self.create_widgets()
        if room is None:
            self.get_room_list()
        else:
            # delay join until tab init has finished and it's been added to the tabwidget
            self.room = room
            QTimer.singleShot(100, self.join_room)

    def get_room_list(self):
        debug.debug("Requesting room list")
        if self.quitting: return
        self.room_list_request = self.server.manager.post(FormRequest(self.server.url), urlencode({
            "action":"rooms",
            "name":self.server.username,
            "pass":self.server.password}))
        self.room_list_request.error.connect(self.join_failed)
        self.room_list_request.finished.connect(self.do_join)

    def do_join(self):
        if self.room_list_request.error() != QNetworkReply.NoError:
            return
        debug.debug("Got room list")
        room_list = html.document_fromstring(self.bytes_to_str(self.room_list_request.readAll()))
        self.room_list_request.deleteLater()

        # get list of rooms
        # lots of icky html scraping here
        rooms_source = room_list.xpath("/html/body/div/table[2]/tr/td/table/tr")

        rooms = []
        self.rooms_by_id = {}
        for i in rooms_source:
            room = {}
            room["name"] = i.xpath('td[1]/table/tr/td/b')[0].text.strip().strip(",")
            room["id"] = i.forms[0].fields["room"]

            props = i.xpath("td/table/tr/td/b/font | td/table/tr/td/font")
            room["props"] = []
            for j in range(0, len(props), 2):
                prop_key = props[j].text_content().strip().strip(":").lower()
                if (prop_key == "topic") | (("color" in props[j+1].attrib) & ("size" in props[j+1].attrib)):
                    # only the topic has both a colour and size in the font tag
                    prop_val = html_escape(props[j+1].text_content().strip())
                else:
                    prop_val = theme.theme(html.tostring(props[j+1], encoding="unicode"))
                room["props"].append((prop_key, prop_val))

            rooms.append(room.copy())
            self.rooms_by_id[room["id"]] = rooms[-1]

        # create room selection dialog
        room_select = QDialog(parent=self)
        room_select.setWindowTitle("Join Room - PyRook")
        room_select_layout = QGridLayout()
        room_select.setLayout(room_select_layout)

        count = 0
        for i in rooms:
            row_button = IdentifiedButton(i["id"], "Join")
            row_button.pressed.connect(room_select.accept)
            row_button.named_pressed.connect(self.join_room)
            room_select_layout.addWidget(row_button, count, 0)

            row_name = QLabel(i["name"])
            room_select_layout.addWidget(row_name, count, 1)

            row_details_layout = QVBoxLayout()
            room_select_layout.addLayout(row_details_layout, count, 2)

            for j in i["props"]:
                label = QLabel("<b>{key}:</b> {value}".format(key=j[0].capitalize(), value=j[1]))
                label.setWordWrap(True)
                row_details_layout.addWidget(label)

            sep = QFrame()
            sep.setFrameShape(QFrame.HLine)
            room_select_layout.addWidget(sep, count+1, 0, 1, 3)

            count += 2

        room_button_box = QDialogButtonBox(QDialogButtonBox.Cancel)
        room_button_box.rejected.connect(room_select.reject)
        room_button_box.accepted.connect(room_select.accept)

        pub_room_button = IdentifiedButton("newpubroom", "Create Public Room")
        pub_room_button.named_pressed.connect(self.create_new_room)
        room_button_box.addButton(pub_room_button, QDialogButtonBox.AcceptRole)

        priv_room_button = IdentifiedButton("newprivroom", "Create Private Room")
        priv_room_button.named_pressed.connect(self.create_new_room)
        room_button_box.addButton(priv_room_button, QDialogButtonBox.AcceptRole)

        room_select_layout.addWidget(room_button_box, count, 0, 1, 3)

        settings = QSettings()
        geometry = settings.value("join_geometry")
        if geometry:
            room_select.restoreGeometry(geometry)

        res = room_select.exec_()
        if settings_get_bool("config/join_geometry", settings=settings):
            settings.setValue("join_geometry", room_select.saveGeometry())
        if res == QDialog.Rejected:
            self.join_aborted()

    def create_new_room(self, roomtype):
        self.roomtype = roomtype
        self.create_room_request = self.server.manager.post(FormRequest(self.server.url),
            urlencode({
                "action":roomtype,
                "name":self.server.username,
                "pass":self.server.password}))
        self.create_room_request.error.connect(self.create_failed)
        self.create_room_request.finished.connect(self.room_created)

    def room_created(self):
        if self.create_room_request.error() != QNetworkReply.NoError:
            return
        self.create_room_request.deleteLater()
        new_room = html.document_fromstring(self.bytes_to_str(self.create_room_request.readAll()))
        url = new_room.xpath("descendant-or-self::frame[@name = 'list']")
        room_id = parse_qs(url[0].get("src"))["room"][0]
        if self.roomtype == "newprivroom":
            room_name = "Private Room"
        else:
            room_name = "Public Room"
        self.rooms_by_id[room_id] = {"name":room_name}
        debug.debug("Room created with id " + room_id + ", now joining.")
        self.join_room(room_id)

    def join_room(self, room_id=None):
        debug.debug("Joining room")
        if room_id is not None:
            self.room = self.rooms_by_id[room_id]
            self.room_id = room_id
        else:
            self.room_id = self.room["id"]
        self.name = self.room["name"]
        self.parent().parent().setTabText(self.parent().parent().indexOf(self), self.name)
        if self.quitting: return
        if not self.theme:
            self.theme = ThemeEngine(self)

        self.logger = Logger(self.name, self.room_id, self.logging_enabled)

        self.room_join_request = self.server.manager.post(FormRequest(self.server.url), urlencode({
            "action":"enter",
            "name":self.server.username,
            "pass":self.server.password,
            "room":room_id,
            "ts":str(time())}))
        self.room_join_request.error.connect(self.enter_failed)
        self.room_join_request.finished.connect(self.do_enter)

    def do_enter(self):
        if self.room_join_request.error() != QNetworkReply.NoError:
            return
        debug.debug("Entered room, now getting chat frames.")
        self.room_join_request.deleteLater()

        self.chatstream_manager = EncodingManager(parent=self)

        self.user_list_request = None
        self.user_list_timer = QTimer(parent=self)
        self.user_list_timer.timeout.connect(self.get_user_list)
        self.user_list_timer.start(20000)
        self.get_user_list()

        self.get_chatstream()

        self.server.parent().exit_item_added()
        self.input_box.setFocus()

    def get_chatstream(self):
        debug.debug("Opening new chatstream")
        if self.chatstream_timeout:
            self.chatstream_timeout.stop()
            self.chatstream_timeout = None
        self.last_data_timer.stop()
        if self.quitting:
            debug.debug("Quitting, cancelling chatstream open")
            return
        if time() - 2 < self.chatstream_ts:
            # we very recently tried to open a chatstream; sleep before retrying
            debug.debug("Chatstream opened recently, backing off")
            QTimer.singleShot(5000, self.get_chatstream)
            return
        self.chatstream_ts = time()
        self.chatstream_refresh = True
        self.chatstream_in_head = False
        self.chatstream_in_script = False
        self.buff = ""

        self.chatstream_refresh_buff = ""

        try:
            req = FormRequest(QUrl("http://" + self.server.domain + self.server.path + "stream.cgi"))
        except AttributeError as e:
            debug.debug("Attribute error constructing network request", e)
        try:
            self.chatstream_request = self.chatstream_manager.post(req, urlencode({
                "action":"stream",
                "room":self.room_id,
                "name":self.server.username,
                "pass":self.server.password,
                "ts":str(time())}))
        except AttributeError as e:
            debug.debug("Attribute error on request from chatstream manager", e)
            return
        self.chatstream_request.finished.connect(self.chatstream_end_debug)
        self.chatstream_request.finished.connect(self.get_chatstream)
        self.chatstream_request.readyRead.connect(self.chatstream_data)
        self.chatstream_timeout = QTimer()
        self.chatstream_timeout.timeout.connect(self.chatstream_abort_debug)
        self.chatstream_timeout.timeout.connect(self.abort_chatstream_request)
        self.chatstream_timeout.setInterval(1000*(60*10 + 10)) # ten minutes, ten seconds
        self.chatstream_timeout.start()
        debug.debug("New chatstream opened")
        if self.chatstream_request.isFinished():
            debug.debug("New chatstream finished already, wait and retry")
            QTimer.singleShot(10000, self.get_chatstream)

    def chatstream_abort_debug(self):
        debug.debug("Chatstream request auto-aborted after 10 minutes")

    def chatstream_end_debug(self):
        debug.debug("Chatstream closed")

    def chatstream_data(self):
        # get data
        data = self.bytes_to_str(self.chatstream_request.readAll())
        # reset timeout for chatstream data
        self.last_data_timer.start()

        # handle replacing of purged lines
        if self.inline_purging:
            debug.debug("Inlining new purged data")
            # first, get the oldest timestamp in the new data
            ts = self.tsre.search(data)
            if not ts:
                # data so far is lead junk, so ignore
                return

            new_start = self.parse_time(ts.group())
            current_html = "\n".join(self.useful_html)
            for i in self.tsre.finditer(current_html):
                this_ts = self.parse_time(i.group())
                if this_ts >= new_start:
                    # overwrite from this point onwards
                    data = "".join((current_html[:i.start()], data[ts.start():]))
                    redacted = data.replace("pass={}".format(self.server.password), "pass=_redacted_")
                    self.raw_html = [redacted]
                    self.purged_signal.emit(redacted)
                    # strip bits that will annoy the HTML parser
                    bodytag = re.search(r"\<body.*?\>", data, re.M)
                    if bodytag:
                        bodytag = bodytag.group()
                    else:
                        bodytag = "<body>"
                    data = re.sub(r"(\<html\>)|(\<\/html\>)|(\<body.*?\>)|(\<\/body\>)|(\<head\>.*?\<\/head\>)", "", data, flags=re.S)
                    self.useful_html = ["<html>" + bodytag]
                    # clear buffer
                    self.inline_purging = False
                    self.chatstream.setHtml("")
                    self.last_time = ""
                    self.chatstream_refresh = False
                    for i in list(self.msgtab_list.values()):
                        i.msg_stream.setHtml("")
                    break

        # update raw html debug view
        else:
            redacted = data.replace("pass={}".format(self.server.password), "pass=_redacted_")
            self.raw_html.append(redacted)
            self.raw_html_signal.emit(redacted)

        # handle room exits
        m = re.search(r"<script language='JavaScript'>\s+<!--\s+top\.location=([^;]*action=lobby[^;]*);", data)
        if m:
            # returned to lobby
            if "err=20" in m.group(1):
                # this corresponds to a kick
                self.handle_left("kicked")
            else:
                # other errors (timeout, etc)
                self.handle_left()
            return

        # handle stream refreshing - strip existing data
        if self.chatstream_refresh:
            debug.debug("Chatstream refresh handling")
            lines = (self.chatstream_refresh_buff + data).split("\n")
            for i, line in enumerate(lines[:-1]):
                if self.chatstream_in_head:
                    if "</head>" in line:
                        self.chatstream_in_head = False
                    else:
                        continue
                elif "<head>" in line:
                    self.chatstream_in_head = True
                    continue
                elif "<html>" in line:
                    continue
                j = self.tsre.search(line)
                if j:
                    newtime = j.group()
                    if self.compare_time(newtime, self.last_time):
                        # refresh done
                        debug.debug("Chatstream refresh done")
                        data = "\n".join(lines[i:])
                        self.chatstream_refresh_buff = ""
                        self.chatstream_refresh = False
                        break
            else:
                # refresh not done
                self.chatstream_refresh_buff = lines[-1] if lines else ""
                return

        # buffer incomplete lines
        split_data = data.split("\n")
        split_data[0] = self.buff + split_data[0]
        self.buff = split_data.pop(-1)

        # retain stripped html for purging
        self.useful_html.append("\n".join(split_data))

        self.insert_html(split_data)

    def insert_html(self, split_data):
        # parse data for processing
        parsed_data = []
        for i in split_data:
            # strip scripts from data
            if self.chatstream_in_script:
                if "</script>" in i:
                    self.chatstream_in_script = False
                continue
            if "<script" in i:
                self.chatstream_in_script = True
                continue
            d, p, t = self.theme.theme(i, forcetime=self.force_timestamps)
            if d is None:
                continue
            # if line is timestamped, update last timestamp and log line
            if t != "":
                new_last_time = self.parse_time(t)
                if new_last_time:
                    self.last_time = new_last_time
                    self.logger.log(new_last_time, p)

            # process any images
            for j in d.xpath("descendant-or-self::img"):
                src_rel = j.get("src")
                if src_rel.startswith("/"):
                    path = src_rel
                else:
                    path = self.server.path + src_rel

                src = "http://" + self.server.domain + path
                filename = self.server.parent().cache_dir.path() + path
                filename = os.path.splitext(filename)[0]
                # to fix a Qt 4.8 issue, rewrite the path to absolute
                j.set("src", filename)
                foldername = filename.rsplit("/", 1)[0]
                folder = QDir(foldername)
                if not folder.exists():
                    folder.mkpath(foldername)
                if not QFile.exists(filename):
                    debug.debug("Requesting image...")
                    if self.quitting: return
                    req = self.server.manager.get(QNetworkRequest(QUrl(src)))
                    self.image_requests.append((req, filename))
                    req.finished.connect(self.image_received)

                # make alt text mouseover text
                if j.get("alt"):
                    j.set("title", j.get("alt"))

                if "onclick" in j.attrib:
                    # this is an image which, in the web client, expands and contracts
                    # when clicked. make it a link so it can be handled here
                    link = builder.A(href="img://" + filename)
                    j.addprevious(link)
                    link.insert(0, j)

            # process /msgs into external tabs if enabled and feed rest to this tab
            tabindex = -1
            if self.msgtabs in ("tab", "both"):
                # check if this is a /msg and get relevant info if so
                ismsg = re.match(r"^((\*(?P<user>[\w-]+?)(\-\>(?P<users>[\w\-\,\ ]+))?\*)|(\[\-\>(?P<tousers>[\w\-\, ]+)\]))", p, re.U)
                if ismsg:
                    users = []
                    for j in ("user", "users", "tousers"):
                        g = ismsg.group(j)
                        if g:
                            users.extend(g.split(", "))
                    # case insensitively remove current user's name
                    l = [i.lower() for i in users]
                    while self.server.username.lower() in l:
                        index = l.index(self.server.username.lower())
                        del users[index]
                        del l[index]
                    users = frozenset(users)
                    users_nocase = frozenset(l)
                    if not users:
                        # user is /msging themselves to be difficult.
                        users = frozenset([self.server.username])
                        users_nocase = frozenset([self.server.username.lower()])

                    tabwidget = self.parent().parent()
                    if users_nocase not in self.msgtab_list:
                        tab = MessageTab(self.name, users, self, users)
                        self.msgtab_list[users_nocase] = tab
                        index = tabwidget.indexOf(self)
                        tabwidget.insertTab(index + 1, tab, tab.name)
                    tab = self.msgtab_list[users_nocase]
                    if not tab.shown:
                        tab.shown = True
                        tabwidget.insertTab(tabwidget.indexOf(self) + 1, tab, tab.name)
                    tabindex = tabwidget.indexOf(tab)
                    out = html.tostring(d, encoding="unicode")
                    tab.add_msg(out)
                    if self.msgtabs == "both":
                        parsed_data.append(out)
                else:
                    # check matches for join, part, away, back strings
                    status_strings = ["has entered",
                        "is away.",
                        "is back.",
                        "has left",
                        "has intered,"
                        "has lef'.",
                        "be below deck.",
                        "be back in the cabin.",
                        "on saapunut.",
                        "on poissa.",
                        "tuli takaisin.",
                        "on poistunut.",
                        "ist eingetreten.",
                        "ist abwesend.",
                        # encoding here is a bit mangled, but it works
                        "ist zur\xc3\xbcck.",
                        "hat den Raum verlassen.",
                        "introiebat.",
                        "abest.",
                        "adest.",
                        "deserebat.",
                        "har kommet.",
                        "er borte.",
                        "er tilbake.",
                        "har dratt."
                        ]
                    isstatus = re.match(r"(?P<username>[A-Za-z0-9\-]+) ({})".format("|".join(status_strings)), p)
                    out = html.tostring(d, encoding="unicode")
                    if isstatus:
                        user = isstatus.group("username").lower()
                        # copy to all messagetabs containing the relevant user
                        # note that this deliberately does not trigger alerts for
                        # the tabs, since the message is copied to multiple places
                        for i in self.msgtab_list:
                            if user in i:
                                self.msgtab_list[i].add_msg(out)
                    parsed_data.append(out)
            else:
                parsed_data.append(html.tostring(d, encoding="unicode"))

            # handle alerts
            if not p.strip():
                continue
            if re.match(r"^(?:{}\: |\[->)".format(self.server.username), p, re.I):
                # we said this, so we don't want to be alerted about it
                # note: this isn't perfect as it won't catch /me, etc, but these
                # get a whole lot harder to detect reliably, so this will do.
                continue
            for key, value in self.alert_states.items():
                if value == "any":
                    self.alert(key, tabindex)

                elif value == "event":
                    # match regex
                    if self.highlights is not None:
                        if self.highlights.search(p):
                            self.alert(key, tabindex)
                    if self.alert_msgs:
                        if re.match(r"^(\[remote\] )?\*[\w-]+\*|\*[\w-]+\-\>", p):
                            self.alert(key, tabindex)
                        # also match memos
                        memo_strings = [
                            "new memo",
                            "noo memo",
                            "new letter",
                            "uusi muistio",
                            "uuden muistio",
                            "uutta muistio",
                            "neues Memo",
                            "neue Memo",
                            "Novum nunti",
                            "Novus nunti",
                            "Novos nunti",
                            "ny memo",
                            "nye memo"]
                        if re.match(r"\[RinkChat\] .*?({})".format("|".join(memo_strings)), p):
                            self.alert(key, tabindex)

        # insert data
        data = "\n".join(parsed_data)
        with AutoScroll(self.chatstream) as scroll:
            scroll.insert(data)

    def alert(self, dest, tab):
        if self.alert_wait:
            return
        if dest == "tabs":
            tabwidget = self.parent().parent()
            # get tab to be highlighted if necessary
            # check if we're currently on the tab we're supposed to highlight
            # and if not, highlight it
            if tab == -1:
                if tabwidget.currentWidget() == self:
                    return
                index = tabwidget.indexOf(self)
            else:
                if tabwidget.currentIndex() == tab:
                    return
                index = tab
            text = tabwidget.tabText(index)
            if not text.startswith("*"):
                tabwidget.setTabText(index, "*" + text + "*")
        elif (dest == "away") & (self.away):
            QApplication.alert(self)
        elif (dest == "back") & (not self.away):
            QApplication.alert(self)

    def compare_time(self, new, old):
        # validate time
        new = self.parse_time(new)
        if not new:
            return False
        if not old:
            return True

        if new > old:
            return new
        return False

    def parse_time(self, t):
        try:
            # full datetime
            t = datetime.datetime.strptime(str(t), "<!-- %m/%d/%Y, %H:%M:%S -->")
        except ValueError:
            # not a valid time
            return False
        return t

    def image_received(self):
        debug.debug("Image request received")
        image = None
        for i, (req, path) in enumerate(self.image_requests):
            if req.isFinished():
                image, filename = self.image_requests.pop(i)
                break
        else:
            debug.debug("No finished image requests found - oops.")
            return

        file_path = QUrl(filename).toString()
        file_path = os.path.splitext(file_path)[0]
        image_file = QFile(file_path)
        image_file.open(QIODevice.WriteOnly)
        image_file.write(image.readAll())
        image_file.close()

        debug.debug("Saving image to " + file_path)

        # list of all attached streams
        tabs = [self.chatstream] + [i.msg_stream for i in self.msgtab_list.values()]
        for i in tabs:
            # load the resource for each
            with AutoScroll(i):
                i.loadResource(QTextDocument.ImageResource, QUrl(file_path))
                i.document().markContentsDirty(0, i.document().characterCount())

    def handle_left(self, err="other"):
        if self.kicked:
            return

        self.quitting = True
        self.chatstream_request.abort()
        if self.chatstream_timeout:
            self.chatstream_timeout.stop()
            self.chatstream_timeout = None

        self.user_list_timer.stop()
        self.kicked = True

        if err == "kicked":
            ret = QMessageBox.warning(self, "PyRook", "You have been kicked from the room. Would you like to rejoin?", QMessageBox.Yes | QMessageBox.No)
        else:
            ret = QMessageBox.warning(self, "PyRook", "You have left the room. Would you like to rejoin?", QMessageBox.Yes | QMessageBox.No)

        if ret == QMessageBox.Yes:
            self.quitting = False
            self.server.parent().exit_item_done()
            self.room_join_request = self.server.manager.post(FormRequest(self.server.url), urlencode({
                "action":"enter",
                "name":self.server.username,
                "pass":self.server.password,
                "room":self.room_id,
                "ts":str(time())}))
            self.room_join_request.error.connect(self.enter_failed)
            self.room_join_request.finished.connect(self.do_enter)
            self.kicked = False
        else:
            self.leave()

    def get_user_list(self):
        if self.quitting: return
        debug.debug("Getting user list")
        if self.user_list_request:
            try:
                self.user_list_request.finished.disconnect()
            except RuntimeError:
                pass
            debug.debug("User list request timed out")
            QApplication.instance().window.status_bar.setText("Network errors detected ")
            self.user_list_request.abort()
            self.user_list_request.deleteLater()
        self.user_list_request = self.server.manager.post(FormRequest(self.server.url), urlencode({
            "action":"userlist",
            "name":self.server.username,
            "pass":self.server.password,
            "room":self.room_id,
            "ts":str(time())}))
        self.user_list_request.finished.connect(self.display_user_list)

    def display_user_list(self):
        status_bar = QApplication.instance().window.status_bar
        if self.user_list_request.error() != QNetworkReply.NoError:
            if not self.quitting:
                debug.debug("User list request error")
                status_bar.setText("Network errors detected ")
            self.user_list_request.deleteLater()
            self.user_list_request = None
            return
        status_bar.setText("")
        text = self.bytes_to_str(self.user_list_request.readAll())
        self.user_list_request.deleteLater()
        self.user_list_request = None

        if "You have been kicked from the room." in text:
            self.handle_left("kicked")
            return
        #TODO minor find error message on timeout or whatever and look for that too
        # (should still be caught from chatstream, just something to keep an eye out for)

        try:
            parse = html.fromstring(text)
        except XMLSyntaxError as err:
            debug.debug("XML Syntax Error: " + str(err) + " in: " + text)
            return

        # get topic
        topic = parse.xpath("/html/body/div/p/b/font[2]")
        if topic:
            topic = topic[0]
            # linkify URLs
            items = re.split(r"(https?\:\/\/\S+)", topic.text)
            topic.text = items[0]
            for i in range(1, len(items), 2):
                # build url to ensure it's parsed correctly
                url = self.server.url.toString() + "?" + urlencode({"action":"link", "url":items[i]})
                a = builder.A(items[i], href=url)
                a.tail = items[i+1]
                topic.insert(i//2, a)

        users = []
        for i in parse.xpath("/html/body/div/table/tr/td"):
            namepath = i.xpath("b[1] | font/b[1]")
            if not namepath:
                # if we hit a line without this in, we're off the end of the actual
                # userlist
                break
            name = html.tostring(namepath[0], method="text", encoding="unicode").strip()
            users.append(name)
            tags = i.xpath("font")
            tagstext = dict(zip((html.tostring(j, method="text", encoding="unicode").strip() for j in tags), tags))
            # away status
            if name.lower() == self.server.username.lower():
                for tag in tagstext:
                    # this is not fully i18n safe, but the only other option relies on
                    # the colour theme instead so there's not much I can do
                    # this covers most available languages
                    # this is also vulnerable to people labelling themselves "away", etc
                    # the only way to account for this is colours, and it seems unlikely
                    # that anyone would label themselves away without wanting to be
                    # treated as away, soo....
                    if tag in ("[{}]".format(i) for i in ("away", "below deck", "poissa", "abwesend", "abest", "borte")):
                        self.away = True
                        break
                else:
                    self.away = False
                self.color_input_box()

            # ips
            if self.geolocate:
                for tag in tagstext:
                    ip = self.IP_re.match(tag)
                    if ip:
                        location = QApplication.instance().lookup_ip(ip.group("ip"))
                        if location:
                            tagstext[tag].attrib["title"] = location

        self.set_users(users)
        for i in self.msgtab_list.values():
            i.users_online(users)

        if self.name == "Loading...":
            # tab isn't named yet, so do so
            self.name = parse.xpath("/html/body/div/nobr/b/font")[0].text
            self.parent().parent().setTabText(self.parent().parent().indexOf(self), self.name)
            if self.logger is not None:
                self.logger.set_name(self.name)

        text = self.theme.theme(html.tostring(parse, encoding="unicode"), notime=True)
        self.user_list.setHtml(text)
        debug.debug("Finished handling user list")

    def set_users(self, users):
        if not users:
            current = "* Public"
        else:
            users.sort()
            current = self.msg_target.currentText()
        users = ["* Public", "* Bots"] + users

        n = self.msg_target.count()
        if self.wrong_target:
            # remove the targeted user as they are not sorted, and will screw with
            # the logic if they've rejoined
            self.msg_target.removeItem(n-1)

        current_items = [self.msg_target.itemText(i) for i in range(self.msg_target.count())]

        if (users == current_items) & (not self.wrong_target):
            return

        self.msg_target.setUpdatesEnabled(False)
        # first, remove users who have left
        # iterate backwards to avoid index changing issues
        for i in range(len(current_items)-1, -1, -1):
            if current_items[i] not in users:
                self.msg_target.removeItem(i)

        # now, insert new users
        count = 0
        for i in users:
            if i not in current_items:
                # find index to insert at
                while count < len(current_items):
                    if current_items[count] > i:
                        self.msg_target.insertItem(count, i)
                        break
                    else:
                        count += 1
                else:
                    self.msg_target.addItem(i)

        self.msg_target.setMinimumContentsLength(max(len(i) for i in users) + 2)
        new = self.msg_target.findText(current)
        if new >= 0:
            self.msg_target.setCurrentIndex(new)
            self.wrong_target = False
        else:
            self.msg_target.addItem(current)
            self.msg_target.setCurrentIndex(self.msg_target.count() - 1)
            self.wrong_target = current
        self.msg_target.setUpdatesEnabled(True)

    def check_wrong_target(self, index):
        if self.wrong_target:
            n = self.msg_target.count() - 1
            if n != index:
                self.msg_target.removeItem(n)
                self.wrong_target = False

    def color_input_box(self, text=None):
        # glow hints for /msg targets
        index = self.msg_target.currentIndex()
        if not isinstance(text, str):
            text = self.input_box.text()

        color = None
        if text.strip():
            cmd = text.split(None, 1)[0].lower()
            if cmd in ("/msg","/rmsg"):
                color = "green"
            elif cmd == "/memo":
                color = "orange"
            elif cmd == "/b":
                color = "blue"

        if color == None:
            if index == 1:
                color = "blue"
            elif index > 1:
                color = "green"

        if (color == None) & (self.away_remind):
            if self.away:
                color = "purple"

        if color != self.glow_color:
            self.glow_color = color
            if color == None:
                self.input_box.setStyleSheet("")
            else:
                self.input_box.setStyleSheet("""QPlainTextEdit {
                    border: 3px solid """ + color + """;
                    border-radius: 3px;
                }""")

    def send_msg(self):
        debug.debug("Parsing message")
        msg = self.input_box.text()
        self.input_box.setText("")
        if not msg:
            self.post_msg("")
            return
        if msg[0] != "/":
            target = self.msg_target.currentText()
            if target == self.wrong_target:
                QMessageBox.warning(self, "User not online", target + " is not currently online. You cannot send private messages to them.")
                return
            if target == "* Public":
                pass
            elif target == "* Bots":
                msg = "/b " + msg
            else:
                msg = "/msg " + target + " " + msg
            self.post_msg(msg)
        else:
            self.parse_cmd(msg)

    def parse_cmd(self, msg):
        purge = False
        cmd = msg.split(None, 1)
        if len(cmd) > 1:
            cmd, args = cmd
            cmd = cmd.lower()
        elif len(cmd) > 0:
            cmd = cmd[0].lower()
            args = ""
        else:
            cmd, args = " ", ""
        if cmd == "/purge":
            purge = True
        elif cmd in ("/highfive", "/hi5"):
            msg = "/me HIGH-FIVES " + args + "!"
        elif cmd == "/away":
            self.away = True
        elif cmd == "/back":
            self.away = False

        self.post_msg(msg, purge)

    def post_msg(self, msg, purge=False):
        debug.debug("Posting message")
        try:
            msg = msg.encode("windows-1252")
        except UnicodeEncodeError:
            try:
                msg = msg.encode("utf8")
            except UnicodeEncodeError:
                QMessageBox.warning(self, "PyRook", "Message send failure: encoding failed. Remove unusual characters.")
                return

        if self.quitting: return
        send_msg_request = self.server.manager.post(FormRequest(self.server.url), urlencode({
            "action":"post",
            "name":self.server.username,
            "pass":self.server.password,
            "room":self.room_id,
            "submit_id":str(time()),
            "msg":msg}))
        send_msg_request.finished.connect(self.check_msg_send)
        if purge:
            send_msg_request.finished.connect(self.do_purge)
        if self.alert_wait_enabled:
            self.alert_wait = True
            if self.alert_wait_timer:
                self.alert_wait_timer.stop()
            self.alert_wait_timer = QTimer()
            self.alert_wait_timer.setSingleShot(True)
            self.alert_wait_timer.setInterval(2000)
            self.alert_wait_timer.timeout.connect(self.end_alert_wait)
            self.alert_wait_timer.start()

    def end_alert_wait(self):
        self.alert_wait = False

    def check_msg_send(self):
        req = self.sender()
        if not req:
            return
        if req.error() != QNetworkReply.NoError:
            QApplication.instance().window.status_bar.setText("Network error sending message ")

    def do_purge(self):
        if settings_get_bool("config/inline_purge"):
            self.inline_purging = True
        else:
            self.raw_html = []
            self.useful_html = []
            self.purged_signal.emit("")
            self.chatstream_refresh_buff = ""
            self.chatstream.setHtml("")
            for i in self.msgtab_list.values():
                i.msg_stream.setHtml("")
            self.last_time = ""
        if self.chatstream_request:
            self.chatstream_request.abort()
        elif not self.quitting:
            self.get_chatstream()

    def reload_stream(self):
        debug.debug("Chatstream reload requested")
        if self.chatstream_request:
            self.chatstream_request.abort()
        else:
            debug.debug("No chatstream present")

    def leave(self):
        debug.debug("Received leave request, logging out")
        self.quitting = True
        self.chatstream_request.abort()
        if self.user_list_request:
            self.user_list_request.abort()
        self.leave_request = self.server.manager.post(FormRequest(self.server.url), urlencode({
            "action":"leave",
            "name":self.server.username,
            "pass":self.server.password,
            "room":self.room_id,
            "submit_id":str(time())}))
        self.leave_request.finished.connect(self.server.parent().exit_item_done)
        self.close_tab()

    def abort_chatstream_request(self):
        debug.debug("Aborting chatstream request")
        if self.chatstream_request:
            if self.chatstream_request.isFinished():
                # HACK for windows issues
                # the chatstream request has finished, but failed to start a new one
                debug.debug("Request already finished, starting new one")
                self.get_chatstream()
            else:
                self.chatstream_request.abort()
        else:
            debug.debug("No current chatstream.")

    def close_tab(self):
        debug.debug("Closing tab")
        if self.logger:
            self.logger.close()
        for i in list(self.msgtab_list.values()):
            i.leave()
        del self.msgtab_list
        self.parent().parent().removeTab(self.parent().parent().indexOf(self))

    def last_data_timeout(self):
        debug.debug("Gone 210 seconds without receiving data, refreshing")
        QApplication.instance().window.status_bar.setText("Chatstream timed out, refreshing ")
        self.reload_stream()

    def enter_failed(self):
        self.room_join_request.deleteLater()
        debug.debug("Room join error")
        ret = QMessageBox.warning(self.server.dialog_parent, "Network Error", "There was a network error joining the room. Retry?", QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.join_room(self.room_id)
        else:
            self.close_tab()

    def create_failed(self):
        self.create_room_request.deleteLater()
        ret = QMessageBox.warning(self.server.dialog_parent, "Network Error", "There was a network error creating a new room. Retry?", QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.create_new_room(self.roomtype)
        else:
            self.close_tab()

    def join_aborted(self):
        debug.debug("Room join cancelled")
        self.close_tab()

    def join_failed(self):
        self.room_list_request.deleteLater()
        debug.debug("Room list fetch error")
        ret = QMessageBox.warning(self.server.dialog_parent, "Network Error", "There was a network error fetching the room list. Retry?", QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.get_room_list()
        else:
            self.close_tab()

    def show_find(self):
        self.find.toggle_visible()

    def handle_URL(self, url):
        self.server.handle_URL(url)
        self.input_box.setFocus()

    def settings_changed(self):
        settings = QSettings()
        self.alert_states = {}
        for column in ("back", "away", "tabs"):
            self.alert_states[column] = settings.value("config/notify_" + column, "never")
        self.alert_msgs = settings_get_bool("config/msgs", True, settings=settings)
        hstr = settings.value("config/highlights", "")
        if hstr:
            if hstr[0] == "~":
                # regex
                try:
                    self.highlights = re.compile(hstr[1:])
                except re.error:
                    self.highlights = None
            else:
                # comma-separated list
                regex = r"(^|[^\w-])(" + "|".join(i.lower().strip() for i in hstr.split(",")) + r")([^\w-]|$)"
                debug.debug("Built highlights regex:", regex)
                self.highlights = re.compile(regex, re.I)
        else:
            self.highlights = None

        self.alert_wait_enabled = settings_get_bool("config/alert_wait", settings=settings)

        self.away_remind = settings_get_bool("config/away_remind", settings=settings)

        self.geolocate = settings_get_bool("config/geolocate", settings=settings)

        self.logging_enabled = settings_get_bool("config/logging", settings=settings)
        if self.logger is not None:
            self.logger.set_enabled(self.logging_enabled)

        if self.theme is not None:
            self.theme.set_font()

        self.msgtabs = settings.value("config/msgtabs", "room")

    def create_widgets(self):
        # create widgets
        self.chatstream = LinkTextBrowser(self.server, parent=self)
        self.chatstream.setOpenExternalLinks(True)
        self.chatstream.setOpenLinks(False)
        self.chatstream.setSearchPaths([self.server.parent().cache_dir.path()])
        self.chatstream.anchorClicked.connect(self.handle_URL)

        self.force_timestamps = False
        self.timestamp_action = QAction("Force timestamps", self)
        self.timestamp_action.setCheckable(True)
        self.timestamp_action.setShortcuts([QKeySequence("F2"), QKeySequence("Ctrl+S")])
        self.timestamp_action.toggled.connect(self.toggle_timestamps)
        self.chatstream.timestamp_action = self.timestamp_action
        self.addAction(self.timestamp_action)

        self.find = Find(self.chatstream)

        self.user_list = QTextBrowser(parent=self)
        self.user_list.setOpenExternalLinks(True)
        self.user_list.setOpenLinks(False)
        self.user_list.anchorClicked.connect(self.handle_URL)

        self.msg_target = QComboBox(parent=self)
        # TODO maybe try an editable combobox here to allow user to add comma-separated
        # list of targets?
        self.msg_target.currentIndexChanged[int].connect(self.color_input_box)
        self.msg_target.currentIndexChanged[int].connect(self.check_wrong_target)

        # HACK specify size based on the QComboBox to get something sane.
        self.input_box = SpellingLineEdit(self.msg_target.sizeHint().height() + 2, parent=self)
        self.input_box.returnPressed.connect(self.send_msg)
        self.input_box.textChanged.connect(self.color_input_box)
        self.msg_target.activated.connect(self.input_box.setFocus)
        self.set_users([])

        self.do_layouts()

    def do_layouts(self):
        # create layouts
        self.main_layout = QVBoxLayout()
        self.display_layout = QSplitter()
        self.input_layout = QHBoxLayout()
        self.chatstream_container = QWidget()
        self.chatstream_layout = QVBoxLayout()
        self.chatstream_container.setLayout(self.chatstream_layout)
        self.chatstream_layout.setContentsMargins(0,0,0,0)

        # put things in layouts
        self.main_layout.addWidget(self.display_layout)
        self.main_layout.addLayout(self.input_layout)
        self.chatstream_layout.addWidget(self.chatstream)
        self.chatstream_layout.addWidget(self.find)
        self.display_layout.addWidget(self.chatstream_container)
        self.display_layout.addWidget(self.user_list)
        self.display_layout.setStretchFactor(0, 3)
        self.display_layout.setStretchFactor(1, 1)
        self.input_layout.addWidget(self.input_box)
        self.input_layout.addWidget(self.msg_target)

        self.setLayout(self.main_layout)

    def show_raw_html(self):
        self.raw_html_widget = QPlainTextEdit()
        self.raw_html_widget.setReadOnly(True)
        self.raw_html_widget.setPlainText("".join(self.raw_html))
        self.raw_html_signal.connect(self.raw_html_widget.appendPlainText)
        self.purged_signal.connect(self.raw_html_widget.setPlainText)
        self.raw_html_widget.show()

    def toggle_timestamps(self, enabled):
        debug.debug("Forced timestamps toggled.")
        self.force_timestamps = enabled
        with AutoScroll(self.chatstream):
            self.chatstream.setText("")
            for i in self.msgtab_list.values():
                i.msg_stream.setText("")
            self.insert_html("\n".join(self.useful_html).split("\n"))

    def bytes_to_str(self, b):
        b = b.data()
        try:
            return str(b, encoding="windows-1252")
        except UnicodeDecodeError:
            return str(b, encoding="utf8")


class IdentifiedButton(QPushButton):
    """This is a button that is constructed with a parameter holding some sort of ID
    and provides a signal on being clicked that includes this ID"""
    named_pressed = Signal(str)
    def __init__(self, num, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)
        self.pressed.connect(self.do_named_pressed)
        self.num = num
    def do_named_pressed(self):
        self.named_pressed.emit(self.num)


class EncodingManager(QNetworkAccessManager):
    def post(self, req, data):
        if isinstance(data, str):
            data = data.encode("iso-8859-1", errors="replace")
        return super().post(req, data)
