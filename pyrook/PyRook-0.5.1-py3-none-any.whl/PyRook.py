import os
import shutil
import sys
import platform
from collections import defaultdict
try: import argparse
except ImportError: argparse = None

from .Importer.QtCore import *
from .Importer.QtGui import *
from .Importer.QtNetwork import *
try: import setproctitle
except ImportError: pass
else: setproctitle.setproctitle("pyrook")
import pkg_resources

from .Debug import debug
from .ThemeEngine import theme
from .ChatWindow import ChatWindow
from .Externals import pygeoip
from .SettingsConvenience import settings_get_bool
from . import __version__

class PyRookApplication(QApplication):
    """The QApplication for PyRook.

    Contains a list of each ChatWindow and each Server in the application."""
    settings_changed = Signal()
    def __init__(self, *args, **kwargs):
        QApplication.__init__(self, *args, **kwargs)

        self.setOrganizationName("Sentynel")
        self.setApplicationName("PyRook")

        debug.enabled = settings_get_bool("config/debug", True)
        debug.pdb = settings_get_bool("config/debug_pdb", False)
        debug.debug("PyRook Application started")
        debug.debug("Python version:", sys.version.replace("\n", ""))
        debug.debug("Qt version:", QT_VERSION_STR)
        debug.debug("Platform:", platform.platform())
        debug.debug("PyRook version:", __version__)

        if os.path.split(sys.path[0])[1].startswith("_MEI"):
            # frozen executable
            self.addLibraryPath(sys.path[0])
            os.chdir(sys.path[0])

        self.server = None
        self.window = None

        try:
            self.datadir = QDesktopServices.storageLocation(QDesktopServices.DataLocation)
        except AttributeError:
            # qt5
            self.datadir = QStandardPaths.writableLocation(QStandardPaths.DataLocation)
        if not os.path.exists(self.datadir):
            QDir().mkpath(self.datadir)

        # load icons
        icon = QIcon()
        path = pkg_resources.resource_filename(__name__, "data/pyrook_logo.svg")
        icon.addFile(path)
        self.setWindowIcon(icon)

        self.install_shortcuts()

        try:
            self.cache_dir = QDir(QDesktopServices.storageLocation(QDesktopServices.CacheLocation))
        except AttributeError:
            # qt5
            self.cache_dir = QDir(QStandardPaths.writableLocation(QStandardPaths.CacheLocation))
        debug.debug("Cache location: " + self.cache_dir.path())
        self.cache_dir.mkpath(self.cache_dir.path())

        self.n_exit = 0
        self.quitting = False

        if argparse:
            self.handle_args()
        else:
            self.args = defaultdict(lambda: None)

        self.geolocate_db = None
        self.settings_changed.connect(self.handle_settings_changed)
        self.handle_settings_changed()

        self.setQuitOnLastWindowClosed(False)
        self.lastWindowClosed.connect(self.exit_timeout)

        self.window = ChatWindow(self)
        self.window.show()

    def install_shortcuts(self):
        if platform.system() == "Windows":
            self.shortcut_windows()
        elif platform.system() == "Linux":
            self.shortcut_linux()
        # other platforms are out of luck right now

    def shortcut_windows(self):
        # create shortcut
        appdata = os.environ["APPDATA"]
        path = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "PyRook.lnk")
        if os.path.exists(path):
            return
        # find executable
        ps = os.environ["PATH"].split(";")
        for p in ps:
            try:
                l = os.listdir(p)
            except FileNotFoundError:
                continue
            if "pythonw.exe" in l:
                break
        else:
            p = os.path.split(sys.executable)[0]
            if "pythonw.exe" not in os.listdir(p):
                debug.debug("Error installing shortcut: Couldn't find our binary")
                return
        try:
            from win32com.client import Dispatch
        except ImportError:
            debug.debug("Error installing shortcut: No pywin32 available")
            return

        shell = Dispatch("WScript.shell")
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = os.path.join(p, "pythonw.exe")
        shortcut.Arguments = "-m PyRook"
        shortcut.WorkingDirectory = p
        shortcut.IconLocation = pkg_resources.resource_filename(__name__, "data/pyrook_logo.ico")
        shortcut.save()

    def shortcut_linux(self):
        desktop_dir = os.path.expanduser("~/.local/share/applications")
        icon_dir = os.path.expanduser("~/.local/share/icons/hicolor/scalable/apps")
        if not os.path.exists(icon_dir):
            os.makedirs(icon_dir)
        if not os.path.exists(desktop_dir):
            os.makedirs(desktop_dir)
        icon_path = os.path.join(icon_dir, "pyrook.svg")
        if not os.path.exists(icon_path):
            iconsrcpath = pkg_resources.resource_filename(__name__, "data/pyrook_logo.svg")
            shutil.copy(iconsrcpath, icon_path)
        desktop_path = os.path.join(desktop_dir, "PyRook.desktop")
        if not os.path.exists(desktop_path):
            desktopsrcpath = pkg_resources.resource_filename(__name__, "data/PyRook.desktop")
            # annoyingly, KDE5 doesn't seem to parse user icon dirs like it should, so we have to
            # manually write the absolute path into the desktop file
            with open(desktopsrcpath) as f:
                desktop = f.read()
            desktop = desktop.replace("Icon=pyrook", "Icon=" + icon_path)
            with open(desktop_path, "w") as f:
                f.write(desktop)
            #shutil.copy(desktopsrcpath, desktop_path)

    def close_all(self):
        debug.debug("close_all called")
        self.quitting = True
        self.window.close()
        self.check_exit_requests()

    def exit_item_added(self):
        self.n_exit += 1

    def exit_item_done(self):
        # this is used to count network operations which should be completed before the
        # application exits
        self.n_exit -= 1
        debug.debug("Exit item done, remaining: " + str(self.n_exit))
        if self.quitting:
            self.check_exit_requests()

    def check_exit_requests(self):
        if self.n_exit == 0:
            debug.debug("No remaining exit items, quitting.")
            self.quit()

    def commitData(self, sm):
        self.closeAllWindows()

    def exit_timeout(self):
        # timeout for leave requests in case of network issues etc
        QTimer.singleShot(20000, self.quit)

    def handle_args(self):
        parser = argparse.ArgumentParser(description="RookChat client")
        parser.add_argument("-u", "--username", help="Your login username")
        parser.add_argument("-p", "--password", help="Your login password")
        parser.add_argument("-s", "--server", help="Full URL for the RookChat server to connect to, e.g. http://www.rinkworks.com/rinkchat/ (the default)")
        parser.add_argument("-n", "--server-name", help="Name of the server to connect to")
        parser.add_argument("other", help="Standard Qt arguments", nargs="*")
        args, leftover = parser.parse_known_args(self.arguments())
        self.args = vars(args)

    def handle_settings_changed(self):
        # install proxy if applicable
        settings = QSettings()
        if settings_get_bool("config/proxy", settings=settings):
            debug.debug("Installing proxy")
            if settings.value("config/proxy_type") == "HTTP":
                ptype = QNetworkProxy.HttpCachingProxy
            else:
                ptype = QNetworkProxy.Socks5Proxy
            try:
                port = int(settings.value("config/proxy_port"))
            except ValueError:
                port = 0
            proxy = QNetworkProxy(ptype,
                                  settings.value("config/proxy_hostname",""),
                                  port,
                                  settings.value("config/proxy_username",""),
                                  settings.value("config/proxy_password",""))
        else:
            proxy = QNetworkProxy(QNetworkProxy.NoProxy)
        QNetworkProxy.setApplicationProxy(proxy)
        # geolocation
        self.geolocate = settings_get_bool("config/geolocate", settings=settings)
        if (self.geolocate) & (self.geolocate_db is None) & (pygeoip is not None):
            dbpath = os.path.join(self.datadir, "GeoIP.dat")
            try:
                self.geolocate_db = pygeoip.GeoIP(dbpath, pygeoip.MEMORY_CACHE)
            except (pygeoip.GeoIPError, IOError):
                debug.debug("Could not open GeoIP database.")
        elif not self.geolocate:
            self.geolocate_db = None

    def lookup_ip(self, ip):
        if not self.geolocate:
            return None
        if not self.geolocate_db:
            return None
        try:
            country = self.geolocate_db.country_name_by_addr(ip)
        except (pygeoip.GeoIPError, TypeError):
            country = ""
        try:
            region = self.geolocate_db.region_by_addr(ip)["region_name"]
        except (pygeoip.GeoIPError, KeyError, TypeError):
            region = ""
        if all((country, region)):
            return ", ".join((region, country))
        else:
            return "".join((region, country))


def main():
    if platform.system() == "Windows":
        # crashes trying to write to stdout in a GUI mode Windows application
        sys.stderr = open(os.devnull, "w")
        sys.stdout = open(os.devnull, "w")
    pyrook = PyRookApplication(sys.argv)

    pyrook.exec_()
