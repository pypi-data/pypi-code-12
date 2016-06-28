#!/usr/bin/env python3
"""
Entry point of HackEdit.
"""
import logging
import os
import shutil
import sys

from PyQt5 import QtCore, QtGui, QtWidgets

import hackedit
vendor = os.environ.get('HACKEDIT_VENDOR_PATH')
if not vendor:
    vendor = os.path.join(os.path.dirname(hackedit.__file__), 'vendor')
    os.environ['HACKEDIT_VENDOR_PATH'] = vendor
sys.path.insert(0, vendor)
os.environ['PATH'] = vendor + os.pathsep + os.environ['PATH']


def setup_sqlite3():
    if sys.platform == 'win32':
        # copy _sqlite3.pyd next to our own sqlite3.dll (with fts4 support enabled)
        pyd = os.path.join(os.path.dirname(sys.executable), 'DLLs', '_sqlite3.pyd')
        try:
            shutil.copy(pyd, vendor)
        except PermissionError:
            # already copied and in use
            pass
        # select the correct sqlite3 dll at runtime depending on the bitness of
        # the python intepreter, see github issue #75
        bitness = 64 if sys.maxsize > 2**32 else 32
        src_dll = os.path.join(vendor, 'sqlite3-%dbits.dll' % bitness)
        dst_dll = os.path.join(vendor, 'sqlite3.dll')
        try:
            shutil.copy(src_dll, dst_dll)
        except PermissionError:
            # already copied and in use
            pass


setup_sqlite3()


from hackedit import __version__                  # noqa
from hackedit.api import system                   # noqa

# Use a file for stdout/stderr if sys.stdout/sys.stderr is None
# This happens when running the app on Windows with pythow.exe or when
# running from the native launcher.
app_data = system.get_app_data_directory()
stdout_path = os.path.join(app_data, 'stdout-pid%d' % os.getpid())
stderr_path = os.path.join(app_data, 'stderr-pid%d' % os.getpid())
if sys.stdout is None:
    sys.stdout = open(stdout_path, 'w')
if sys.stderr is None:
    sys.stderr = open(stderr_path, 'w')

from hackedit.api.gettext import get_translation  # noqa
from hackedit.app import argparser, logger        # noqa
import faulthandler                               # noqa


try:
    faulthandler.enable()
except RuntimeError:
    # no stderr, happens on windows with the native launcher
    logging.exception('failed to enable faulthandler')


def main():
    """
    Application entry point, runs the application
    """
    # parse command line args
    args = argparser.parse_args()
    if args.log:
        # print the last application log
        try:
            with open(logger.get_path(), 'r') as f:
                print(f.read())
        finally:
            sys.exit(0)
    if args.version:
        # print versions
        from hackedit.api.versions import versions_str
        print(versions_str())
        sys.exit(0)

    # tell pyqode that we use the PyQt5 API.
    os.environ['QT_API'] = 'pyqt5'

    # Setup Qt Application
    qapp = QtWidgets.QApplication(sys.argv)
    qapp.setOrganizationName('HackEdit')
    qapp.setOrganizationDomain('hackedit.com')
    qapp.setApplicationDisplayName('HackEdit')
    qapp.setApplicationName('HackEdit')
    qapp.setApplicationVersion(__version__)

    get_translation()

    # setup logger
    from hackedit.app import settings
    settings.load()

    log_level = settings.log_level()
    # override log level
    if args.log_level:
        log_level = args.log_level
    elif args.verbose:
        log_level = logging.DEBUG
    logger.setup(log_level)

    _logger().info('starting up...')

    # Setup splash screen
    if settings.show_splashscreen():
        from hackedit.app.forms import hackedit_rc
        assert hackedit_rc

        pixmap = QtGui.QPixmap(':/splashscreen.png')
        splash = QtWidgets.QSplashScreen(pixmap)
        splash.show()
        splash.raise_()
        qapp.processEvents()

        splash.showMessage(_('Loading application module'),
                           QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter,
                           QtCore.Qt.white)
        qapp.processEvents()

    else:
        splash = None

    # Setup hackedit application, this may take a while as we have
    # to load all plugin entry points, load the icon theme,...
    from hackedit.app.application import Application
    app = Application(qapp, splash, args)

    # Run the application!
    _logger().info('running...')
    app.run()

    # remove temporary stdout/stderr
    try:
        sys.stdout.close()
        os.remove(stdout_path)
    except OSError:
        pass
    try:
        sys.stderr.close()
        os.remove(stderr_path)
    except OSError:
        pass


def _logger():
    return logging.getLogger(__name__)


if __name__ == '__main__':
    main()
