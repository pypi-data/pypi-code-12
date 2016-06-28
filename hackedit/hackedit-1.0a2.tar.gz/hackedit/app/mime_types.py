"""
This module contains a small API built on top of the python mimetypes module
to manipulate user defined mimetypes.
"""
import json
import mimetypes
import pkg_resources

from PyQt5 import QtCore
from pygments.lexers import get_all_lexers, get_lexer_for_mimetype
from pyqode.core.widgets import SplittableCodeEditTabWidget


# monkeypatch pygments.plugin.find_plugin_lexers
def find_plugin_lexers():
    """
    Copy of pygments.plugins.find_plugin_lexers to avoid RequirementParseError
    (issue introduced in setuptools 20.2)
    """
    if pkg_resources is None:
        return
    for entrypoint in pkg_resources.iter_entry_points('pygments.lexers'):
        try:
            yield entrypoint.load()
        except pkg_resources.RequirementParseError:
            continue
from pygments import plugin  # noqa
plugin.find_plugin_lexers = find_plugin_lexers
# execute it once to make sure the cache is built using our monkeypatched
# function
list(plugin.find_plugin_lexers())


def load():
    """
    Loads user defined mimetypes and extension into standard module.

    This function is called once on startup by the application and can be
    called later to update the mimetypes db.
    """
    string = QtCore.QSettings().value('editor/mimetypes', '{}')
    db = json.loads(string)
    if not db:
        db = _get_default_mimetypes()
        QtCore.QSettings().setValue('editor/mimetypes', json.dumps(db))
    for mimetype, exts in db.items():
        if not exts:
            continue
        for ext in exts:
            mimetypes.add_type(mimetype, ext.replace('*', ''))


def _get_default_mimetypes():
    ret_val = {}
    for mtype in get_supported_mimetypes():
        exts = get_extensions(mtype)
        ret_val[mtype] = exts
    return ret_val


def get_supported_mimetypes():
    """
    Returns the list of supported mimetypes.

    This list is build up on the list of editor plugins and their supported
    mimetypes.
    """
    keys = SplittableCodeEditTabWidget.editors.keys()
    ret_val = []
    for k in keys:
        ret_val.append(k)
    # all other mimetypes are handled by the fallback editor
    for _, _, filenames, mtypes in get_all_lexers():
        if len(mtypes) and len(filenames):
            ret_val.append(mtypes[0])
    return list(set(ret_val))


def get_handler(mimetype):
    """
    Get the handler (editor) for a given mimetype.
    """
    try:
        return SplittableCodeEditTabWidget.editors[mimetype]
    except KeyError:
        return SplittableCodeEditTabWidget.fallback_editor


def get_extensions(mimetype):
    """
    Gets the list of extensions for a given mimetype. This function
    will return both the builtin extensions and the user defined extensions.
    """
    string = QtCore.QSettings().value('editor/mimetypes', '{}')
    db = json.loads(string)
    try:
        custom = db[mimetype]
    except KeyError:
        try:
            l = get_lexer_for_mimetype(mimetype)
        except Exception:
            custom = ['*%s' % ext for ext in
                      mimetypes.guess_all_extensions(mimetype)]
        else:
            custom = l.filenames
    return sorted([ext for ext in set(custom) if ext])


def set_extensions(mimetype, extensions):
    """
    Sets the list of user defined extension for a given mimetype.

    This mapping is stored in QSettings. Use :func:`load` to apply the new
    types.

    :param mimetype: The mimetype to add. If the extension
    :param extension: the extension to map with mimetype.
    """
    string = QtCore.QSettings().value('editor/mimetypes', '{}')
    db = json.loads(string)
    db[mimetype] = sorted(extensions)
    QtCore.QSettings().setValue('editor/mimetypes', json.dumps(db))
    if mimetype not in mimetypes.types_map.values():
        for ext in extensions:
            mimetypes.add_type(mimetype, ext.replace('*', ''))


def reset_custom_extensions():
    """
    Resets custom extensions, only builtins will be kept
    """
    QtCore.QSettings().setValue('editor/mimetypes', '{}')
