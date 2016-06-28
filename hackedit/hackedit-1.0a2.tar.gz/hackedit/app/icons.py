"""
This module contains utility function to retrieve common icons.

Icons are always loaded from an icon theme (the system icon theme on Linux
and the embedded Breeze theme on Windows and OSX)
"""
import logging
import os
import sys

from PyQt5.QtGui import QIcon

from hackedit.api import system
from hackedit.app import settings


ORIGINAL_THEME_NAME = QIcon.themeName()


def icon_themes():
    themes = []
    for path in QIcon.themeSearchPaths():
        try:
            dirs = os.listdir(path)
        except OSError:
            _logger().debug('failed to list icons in path %r', path)
        else:
            for d in dirs:
                pth = os.path.join(path, d)
                if os.path.isfile(pth):
                    continue
                try:
                    files = os.listdir(pth)
                except OSError:
                    pass
                else:
                    if 'cursors' not in files and 'index.theme' in files:
                        themes.append(d)
    return sorted(list(set(themes)))


def system_icon_theme():
    """
    Gets the system icon theme (this is only usefull on linux).
    """
    theme = QIcon.themeName()
    if theme == '':
        if system.LINUX:
            theme = 'default'
        else:
            theme = 'breeze'
    return theme


def init():
    name = settings.icon_theme()

    paths = QIcon.themeSearchPaths()
    paths.append(os.path.join(sys.prefix, 'share', 'hackedit', 'icons'))
    paths.append('/usr/local/share/hackedit/icons')
    QIcon.setThemeSearchPaths(list(set(paths)))
    _logger().debug('icon theme path: %r', paths)
    if name:
        QIcon.setThemeName(name)
        _logger().debug('icon theme: %s', name)


def _logger():
    return logging.getLogger(__name__)
