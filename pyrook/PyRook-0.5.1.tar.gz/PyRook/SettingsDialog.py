

from .Importer.QtCore import *
from .Importer.QtGui import *

from .Externals import enchant, hunspell, pygeoip
from .WebTab import WebTab
from .SettingsConvenience import settings_get_bool, settings_set_bool

class SettingsDialog(QDialog):
    changed = Signal()
    def __init__(self, *args):
        QDialog.__init__(self, *args)
        self.setWindowTitle("Configure - PyRook")
        self.settings = QSettings()

        settings_layout = QVBoxLayout()
        self.setLayout(settings_layout)

        tab_widget = QTabWidget()
        settings_layout.addWidget(tab_widget)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        settings_layout.addWidget(self.buttons)
        self.buttons.clicked.connect(self.button_clicked)

        # tabs
        display_tab = QWidget()
        tab_widget.addTab(display_tab, "Display")
        display_layout = QVBoxLayout()
        display_tab.setLayout(display_layout)

        behaviour_tab = QWidget()
        tab_widget.addTab(behaviour_tab, "Behaviour")
        behaviour_layout = QVBoxLayout()
        behaviour_tab.setLayout(behaviour_layout)

        notifications_tab = QWidget()
        tab_widget.addTab(notifications_tab, "Notifications")
        notifications_layout = QVBoxLayout()
        notifications_tab.setLayout(notifications_layout)

        account_tab = QWidget()
        tab_widget.addTab(account_tab, "Account")
        account_layout = QVBoxLayout()
        account_tab.setLayout(account_layout)

        proxy_tab = QWidget()
        tab_widget.addTab(proxy_tab, "Proxy")
        proxy_layout = QVBoxLayout()
        proxy_tab.setLayout(proxy_layout)
        # end tabs

        # display tab
        # appearance
        appearance_frame = QGroupBox("Appearance")
        display_layout.addWidget(appearance_frame)
        appearance_layout = QFormLayout()
        appearance_frame.setLayout(appearance_layout)

        font_layout = QHBoxLayout()
        self.font_display_box = QLineEdit()
        font_layout.addWidget(self.font_display_box)
        self.font_display_box.setEnabled(False)
        self.selected_font = self.settings.value("config/font")
        self.update_font()
        choose_font = QPushButton("Select font")
        font_layout.addWidget(choose_font)
        choose_font.pressed.connect(self.show_font_chooser)
        default_font = QPushButton("Default")
        font_layout.addWidget(default_font)
        default_font.pressed.connect(self.reset_font)
        appearance_layout.addRow("Font", font_layout)

        self.join_geometry = QCheckBox("Save join window size")
        self.join_geometry.setChecked(settings_get_bool("config/join_geometry", settings=self.settings))
        appearance_layout.addRow(self.join_geometry)

        self.away_remind = QCheckBox("Purple input box when away")
        self.away_remind.setChecked(settings_get_bool("config/away_remind", settings=self.settings))
        appearance_layout.addRow(self.away_remind)

        self.local_time = QCheckBox("Show timestamps in local time")
        self.local_time.setChecked(settings_get_bool("config/local_time", settings=self.settings))
        appearance_layout.addRow(self.local_time)
        # end appearance

        # /msg
        msg_frame = QGroupBox("Private messages")
        display_layout.addWidget(msg_frame)
        msg_layout = QFormLayout()
        msg_frame.setLayout(msg_layout)

        self.msg_room = QRadioButton("Show in main room", msg_frame)
        self.msg_tab = QRadioButton("Show in separate tab", msg_frame)
        self.msg_both = QRadioButton("Show in both", msg_frame)
        msg_layout.addRow(self.msg_room)
        msg_layout.addRow(self.msg_tab)
        msg_layout.addRow(self.msg_both)
        msg_setting = self.settings.value("config/msgtabs", "room")
        if msg_setting == "tab":
            self.msg_tab.setChecked(True)
        elif msg_setting == "both":
            self.msg_both.setChecked(True)
        else:
            self.msg_room.setChecked(True)
        # end /msg
        # end display

        # behaviour tab
        # features
        features_frame = QGroupBox("Features")
        behaviour_layout.addWidget(features_frame)
        features_layout = QFormLayout()
        features_frame.setLayout(features_layout)

        self.check_spelling = QCheckBox("Check spelling")
        self.check_spelling.setChecked(settings_get_bool("config/spelling", settings=self.settings))
        self.check_spelling.setEnabled(enchant is not None or hunspell is not None)
        features_layout.addRow(self.check_spelling)

        self.web_tabs = QCheckBox("Open internal URLs in tabs")
        self.web_tabs.setEnabled(WebTab is not None)
        self.web_tabs.setChecked(settings_get_bool("config/web_tabs", settings=self.settings))
        features_layout.addRow(self.web_tabs)

        self.inline_purge = QCheckBox("Retain older messages on purge")
        self.inline_purge.setChecked(settings_get_bool("config/inline_purge", True, settings=self.settings))
        features_layout.addRow(self.inline_purge)
        # end features

        # logging
        self.logging_frame = QGroupBox("Log conversations to disk")
        behaviour_layout.addWidget(self.logging_frame)
        logging_frame_layout = QFormLayout()
        self.logging_frame.setLayout(logging_frame_layout)
        self.logging_frame.setCheckable(True)
        self.logging_frame.setChecked(settings_get_bool("config/logging", settings=self.settings))

        self.log_rotation = QComboBox()
        rotation_items = ["Daily", "Monthly", "Yearly", "Never"]
        self.log_rotation.addItems(rotation_items)
        rotation_val = self.settings.value("config/log_rotation", "Monthly")
        self.log_rotation.setCurrentIndex(rotation_items.index(rotation_val if rotation_val in rotation_items else "Monthly"))
        logging_frame_layout.addRow("Switch log file", self.log_rotation)
        # end logging

        # op tools
        op_frame = QGroupBox("Op Tools")
        behaviour_layout.addWidget(op_frame)
        op_layout = QFormLayout()
        op_frame.setLayout(op_layout)

        self.geolocate = QCheckBox("Geolocate IPs")
        self.geolocate.setChecked(settings_get_bool("config/geolocate", settings=self.settings))
        self.geolocate.setEnabled(pygeoip is not None)
        op_layout.addRow(self.geolocate)
        # end op tools
        # end behaviour

        # notifications tab
        # radio buttons
        radio_frame = QGroupBox("Conditions")
        notifications_layout.addWidget(radio_frame)
        radio_layout = QGridLayout()
        radio_frame.setLayout(radio_layout)

        radio_desc = QLabel("Specify the conditions in which window highlight alerts while present or away and tab label highlights should be shown.")
        radio_desc.setWordWrap(True)
        radio_layout.addWidget(radio_desc, 0, 0, 1, 4)

        self.radio_row_names = ("any", "event", "never")
        self.radio_column_names = ("back", "away", "tabs")

        for row, label in enumerate(("Any message", "Specified events", "Never"), 2):
            radio_layout.addWidget(QLabel(label), row, 0)

        self.notify_buttons = []
        for column, label in enumerate(("Present", "Away", "Tabs"), 1):
            radio_layout.addWidget(QLabel(label), 1, column)
            buttons = []
            group = QButtonGroup(parent=notifications_tab)
            for row in range(2, 5):
                button = QRadioButton()
                buttons.append(button)
                group.addButton(button)
                radio_layout.addWidget(button, row, column)
            enabled = self.settings.value("config/notify_" + self.radio_column_names[column-1], "never")
            buttons[self.radio_row_names.index(enabled)].setChecked(True)
            self.notify_buttons.append(buttons[:])
        # end radio buttons

        # events
        events_frame = QGroupBox("Events")
        notifications_layout.addWidget(events_frame)
        events_layout = QFormLayout()
        events_frame.setLayout(events_layout)

        self.alert_highlights = QLineEdit()
        events_layout.addRow("On mention of words", self.alert_highlights)
        info = "Comma-separated list of keywords"
        self.alert_highlights.setValidator(QRegExpValidator(QRegExp(r"(\~.*)|([\w\-\,]*)"), self.alert_highlights))
        self.alert_highlights.setPlaceholderText(info)
        self.alert_highlights.setToolTip(info)
        alert_highlights = self.settings.value("config/highlights", "")
        if isinstance(alert_highlights, QPyNullVariant):
            alert_highlights = ""
        self.alert_highlights.setText(alert_highlights)

        self.alert_msgs = QCheckBox("On received /msg or /memo")
        events_layout.addRow(self.alert_msgs)
        self.alert_msgs.setChecked(settings_get_bool("config/msgs", True, settings=self.settings))
        # end events

        # misc
        misc_frame = QGroupBox("Block alerts")
        notifications_layout.addWidget(misc_frame)
        misc_layout = QFormLayout()
        misc_frame.setLayout(misc_layout)

        self.alert_wait = QCheckBox("Immediately after posting")
        misc_layout.addRow(self.alert_wait)
        self.alert_wait.setChecked(settings_get_bool("config/alert_wait", settings=self.settings))
        # end misc
        # end notifications

        # account tab
        saved_details_frame = QGroupBox("Saved details")
        account_layout.addWidget(saved_details_frame)
        saved_details_layout = QFormLayout()
        saved_details_frame.setLayout(saved_details_layout)

        self.username = QLineEdit(self.settings.value("account/username", ""))
        self.password = QLineEdit(self.settings.value("account/password", ""))
        self.password.setEchoMode(QLineEdit.Password)
        saved_details_layout.addRow("Username", self.username)
        saved_details_layout.addRow("Password", self.password)
        # end account tab

        # proxy tab
        self.proxy_frame = QGroupBox("Use proxy")
        proxy_layout.addWidget(self.proxy_frame)
        proxy_frame_layout = QFormLayout()
        self.proxy_frame.setLayout(proxy_frame_layout)
        self.proxy_frame.setCheckable(True)
        self.proxy_frame.setChecked(settings_get_bool("config/proxy", settings=self.settings))

        self.proxy_type = QComboBox()
        proxy_frame_layout.addRow("Type", self.proxy_type)
        types = ["HTTP", "SOCKS5"]
        self.proxy_type.addItems(types)
        try:
            self.proxy_type.setCurrentIndex(types.index(self.settings.value("config/proxy_type", "HTTP")))
        except ValueError:
            pass

        self.proxy_hostname = QLineEdit()
        proxy_frame_layout.addRow("Hostname", self.proxy_hostname)
        self.proxy_hostname.setText(self.settings.value("config/proxy_hostname", ""))

        self.proxy_port = QLineEdit()
        proxy_frame_layout.addRow("Port", self.proxy_port)
        self.proxy_port.setValidator(QIntValidator(1,65535, self.proxy_port))
        self.proxy_port.setText(self.settings.value("config/proxy_port", "8080"))

        self.proxy_username = QLineEdit()
        proxy_frame_layout.addRow("Username", self.proxy_username)
        self.proxy_username.setText(self.settings.value("config/proxy_username", ""))

        self.proxy_password = QLineEdit()
        proxy_frame_layout.addRow("Password", self.proxy_password)
        self.proxy_password.setText(self.settings.value("config/proxy_password", ""))
        # end proxy

    def button_clicked(self, button):
        role = self.buttons.standardButton(button)
        if role in (QDialogButtonBox.Apply, QDialogButtonBox.Ok):
            # apply settings

            # display
            self.settings.setValue("config/font", self.selected_font)
            settings_set_bool("config/join_geometry", self.join_geometry.isChecked(), self.settings)
            if not self.join_geometry.isChecked():
                # clear any previously set join geometry
                self.settings.setValue("join_geometry", "")
            settings_set_bool("config/away_remind", self.away_remind.isChecked(), self.settings)
            settings_set_bool("config/local_time", self.local_time.isChecked(), self.settings)

            #settings_set_bool("config/msgtabs", self.msgtabs.isChecked(), self.settings)
            if self.msg_tab.isChecked():
                msg_setting = "tab"
            elif self.msg_both.isChecked():
                msg_setting = "both"
            else:
                msg_setting = "room"
            self.settings.setValue("config/msgtabs", msg_setting)
            # end display

            # behaviour
            settings_set_bool("config/spelling", self.check_spelling.isChecked(), self.settings)
            settings_set_bool("config/web_tabs", self.web_tabs.isChecked(), self.settings)
            settings_set_bool("config/inline_purge", self.inline_purge.isChecked(), self.settings)

            settings_set_bool("config/logging", self.logging_frame.isChecked(), self.settings)
            self.settings.setValue("config/log_rotation", self.log_rotation.currentText())

            settings_set_bool("config/geolocate", self.geolocate.isChecked(), self.settings)
            # end behaviour

            # notifications
            for i, column in enumerate(self.notify_buttons):
                for j, button in enumerate(column):
                    if button.isChecked():
                        self.settings.setValue("config/notify_" + self.radio_column_names[i], self.radio_row_names[j])
                        break

            self.settings.setValue("config/highlights", self.alert_highlights.text())
            settings_set_bool("config/msgs", self.alert_msgs.isChecked(), self.settings)
            settings_set_bool("config/alert_wait", self.alert_wait.isChecked(), self.settings)
            # end notifications

            # account
            self.settings.setValue("account/username", self.username.text())
            self.settings.setValue("account/password", self.password.text())
            # end account

            # proxy
            settings_set_bool("config/proxy", self.proxy_frame.isChecked(), self.settings)
            if self.proxy_frame.isChecked():
                self.settings.setValue("config/proxy_type", self.proxy_type.currentText())
                self.settings.setValue("config/proxy_hostname", self.proxy_hostname.text())
                self.settings.setValue("config/proxy_port", self.proxy_port.text())
                self.settings.setValue("config/proxy_username", self.proxy_username.text())
                self.settings.setValue("config/proxy_password", self.proxy_password.text())
            # end proxy

            self.changed.emit()

        if role == QDialogButtonBox.Ok:
            self.accept()

        elif role == QDialogButtonBox.Cancel:
            self.reject()

    def update_font(self):
        if not self.selected_font:
            self.font_display_box.setText("default")
            return
        self.font_display_box.setText("{} {}".format(self.selected_font.family(), self.selected_font.pointSize()))

    def show_font_chooser(self):
        if self.selected_font:
            font, choice = QFontDialog.getFont(self.selected_font, self)
        else:
            font, choice = QFontDialog.getFont(self)
        if not choice:
            return
        self.selected_font = font
        self.update_font()

    def reset_font(self):
        self.selected_font = None
        self.update_font()
