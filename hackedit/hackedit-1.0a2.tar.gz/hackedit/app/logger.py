"""
This module contains functions for easily setup the application logger
"""
import glob
import logging
import os

import coloredlogs

from hackedit.api import system

#: reference to the file handler
file_handler = None


FIELD_STYLES = dict(
    asctime=dict(color='green'),
    hostname=dict(color='magenta'),
    levelname=dict(color='cyan', bold=True),
    programname=dict(color='cyan'),
    name=dict(color='blue'))

LEVEL_STYLES = dict(
    debug=dict(color='green'),
    info=dict(),
    pyqodedebug=dict(color='cyan'),
    pyqodedebugcomm=dict(color='magenta'),
    warning=dict(color='yellow'),
    error=dict(color='red'),
    critical=dict(color='red', bold=True))


def get_path():
    """
    Returns the log file path.

    - GNU/Linux: ``~/.hackedit/hackedit.log``
    - OSX: ``~/Library/Application Support/HackEdit/hackedit.log``
    - WINDOWS: ``%APPDATA%\HackEdit\hackedit.log``

    :return: str
    """
    from hackedit.api import system
    return os.path.join(system.get_app_data_directory(), 'hackedit-%d.log' % os.getpid())


def setup(level=logging.INFO):
    """
    Configures the logger, adds a stream handler and a file handler.

    :param level: log level, default is logging.INFO
    """
    global file_handler
    if len(get_log_files()) > 5:
        clear_logs()
    file_handler = logging.FileHandler(get_path())
    handlers = [
        # a new log will be created on each new day with 5 days backup
        file_handler,
    ]
    fmt = '%(levelname)s %(asctime)s:%(msecs)03d %(name)s[%(process)d]  %(message)s'
    datefmt = '%H:%M:%S'
    logging.basicConfig(
        level=level, handlers=handlers,
        format=fmt, datefmt=datefmt)

    coloredlogs.install(level=level, fmt=fmt, datefmt=datefmt, reconfigure=False,
                        field_styles=FIELD_STYLES, level_styles=LEVEL_STYLES)
    file_handler.setLevel(level)


def clear_logs():
    if file_handler:
        file_handler.close()
    failures = []
    for filename in get_log_files():
        pth = os.path.join(system.get_app_data_directory(), filename)
        try:
            os.remove(pth)
        except OSError:
            if os.path.exists(pth):
                logging.getLogger('open_cobol_ide').exception(
                    'failed to remove log file %r', pth)
                failures.append(pth)
    return failures


def get_log_files():
    return glob.glob(os.path.join(system.get_app_data_directory(), '*.log'))


def get_application_log():
    try:
        with open(get_path(), 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return ''
