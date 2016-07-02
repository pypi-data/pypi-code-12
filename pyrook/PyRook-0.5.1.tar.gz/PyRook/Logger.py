import os
import datetime

from .Importer.QtCore import *

from .Debug import debug
from .ThemeEngine import theme

class Logger(QObject):
    def __init__(self, roomname, roomid, enabled):
        QObject.__init__(self)
        self.roomname = roomname
        self.roomid = roomid
        self.enabled = enabled
        self.file = None
        self.lasttime = None
        self.lastmsg = ""
        self.buffer = []

    def log(self, timestamp, message):
        if not self.enabled:
            return

        if self.roomname == "Loading...":
            # buffer until we have a name
            self.buffer.append((timestamp, message))
            return

        if not self.file:
            self.open()

        # timestamp check to avoid repeat messages on purge
        if self.lasttime:
            if timestamp < self.lasttime:
                return
            elif timestamp == self.lasttime:
                if self.lastmsg == message:
                    return
        self.lasttime = timestamp
        self.lastmsg = message

        self.file.write("<{}> {}\n".format(theme.timestamp_to_local(timestamp).toString("yyyy-MM-dd hh:mm:ss"), message))

    def set_enabled(self, enabled):
        self.enabled = enabled
        if (not enabled) & (self.file is not None):
            self.file.close()
            self.file = None

    def open(self):
        datadir = QCoreApplication.instance().datadir
        folder = os.path.join(datadir, "logs")
        if not os.path.exists(folder):
            try:
                os.mkdir(folder)
            except (OSError, IOError):
                debug.debug("Could not create log folder.")
                return

        # ensure logs are rotated at the desired frequency
        today = datetime.date.today()
        rotate = QSettings().value("config/log_rotation", "Monthly")
        if rotate == "Never":
            timeformat = ""
        elif rotate == "Yearly":
            timeformat = "%Y - "
        elif rotate == "Daily":
            timeformat = "%Y-%m-%d - "
        else:
            timeformat = "%Y-%m - "
        path = os.path.join(datadir, "logs", "{}{} {}.log".format(today.strftime(timeformat), self.roomname, self.roomid))

        debug.debug("Starting logging of", self.roomname, "in", path)
        try:
            self.file = open(path, "a")
        except (OSError, IOError):
            debug.debug("Could not open log file.")
            return
        self.file.write("**** BEGIN LOGGING {}\n\n".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def close(self):
        if not self.file:
            return
        self.file.write("**** END LOGGING {}\n\n\n".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.file.close()

    def set_name(self, name):
        self.roomname = name
        for i in self.buffer:
            self.log(*i)
        self.buffer = []
