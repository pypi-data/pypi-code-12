"""
Provides a series of function on top of gettext to retrieve a particular
translations (used by both the core apps and the plugins).
"""
import logging
import re
import gettext
import os
import sys

from PyQt5 import QtCore

from pyqode.core.api.utils import memoized


@memoized
def get_available_locales():
    """
    Gets the list of available locales (the one for which a get_translation is
    available)
    """
    ret_val = set()
    ret_val.add('default')
    locale_dir = os.path.join(sys.prefix, 'share', 'locale')
    try:
        locales = os.listdir(locale_dir)
    except OSError as e:  # pragma: no cover
        _logger().warn('failed to list translations files of directory %r: %s',
                       locale_dir, e)
    else:
        for d in locales:
            mo_path = os.path.join(locale_dir, d, 'LC_MESSAGES', 'hackedit.mo')
            if os.path.exists(mo_path):
                ret_val.add(d)
    return ret_val


def get_locale():
    """
    Gets the current locale defined in the application settings
    """
    default = 'default'
    return QtCore.QSettings().value('env/locale', default)


def set_locale(locale):
    """
    Sets the application locale
    """
    QtCore.QSettings().setValue('env/locale', locale)


def get_translation(package='hackedit'):
    """
    Gets the get_translation function for the language selected by the user.

    Use this function at the top of each of your plugin modules::

        from hackedit.api.gettext import get_translation
        _ = get_translation(package='hackedit-python')
        _('translatable string')

    :param package: Name of the package to get the get_translation for...

    :returns: None if package == 'hackedit' otherwise return the
        get_translation function usable directly in your module.
    """
    locale_dir = os.path.join(sys.prefix, 'share', 'locale')
    if not os.path.exists(locale_dir):  # pragma: no cover
        locale_dir = os.path.join(
            sys.prefix, 'local', 'share', 'locale')
    try:
        t = gettext.translation(package, localedir=locale_dir,
                                languages=[get_locale()])
        if package == 'hackedit':
            # we can install globally
            t.install()
            return t.gettext
        else:
            return t.gettext
    except OSError:
        t = gettext.NullTranslations()
        if package == 'hackedit':
            # we can install globally
            t.install()
        return t.gettext


def hackedit_gettext_hook(ui_script_path):  # pragma: no cover
    """
    pyqt-distutils hook that will replace Qt translate tools by calls to
    ``hackedit.api.gettext.translation``.
    """
    from pyqt_distutils.config import Config

    with open(ui_script_path, 'r') as fin:
        content = fin.read()

    # replace ``_translate("context", `` by ``_(``
    content = re.sub(r'_translate\(".*",\s', '_(', content)

    # inject the _ function
    cfg = Config()
    cfg.load()
    package_name = cfg.package_name
    content = content.replace(
        '        _translate = QtCore.QCoreApplication.translate',
        '        from hackedit.api.gettext import get_translation\n'
        '        _ = get_translation(package="%s")' % package_name)

    with open(ui_script_path, 'w') as fout:
        fout.write(content)


def _logger():
    return logging.getLogger(__name__)
