"""
This module provides an API for getting shortcuts from application preferences.

You should always :func:`use hackedit.api.shortcuts.get` to get a shortcut.
"""
import json

from PyQt5 import QtCore


def get(name, text, default):
    """
    Gets a shortcut for the given action name, if the name does not exists
    in the shortcuts map, default is used instead.

    The shortcut map is stored in QSettings and can be edited thought the
    application preferences (Environmnent > Shortcuts).

    :param name: Name of the action (non-translatable as it used to identify
                 the action)
    :param text: translatable text of the action
    :param default: Default shortcut value, will be used if the shortcut cannot
                    be found in the map.

    :returns: shortcut string
    """
    global _MAP
    try:
        sh = _MAP[name][_INDEX_VALUE]
    except KeyError:
        sh = default
    if not sh:
        sh = default
    if default is not None:
        _MAP[name] = [sh, default, text]
    # update action text (translation)
    _MAP[name][_INDEX_TEXT] = text
    return sh


def update(name, text, shortcut):
    """
    Updates the shortcut of a given action name.

    This function is called by the shortcuts preference page, yo should never
    have to call it yourself.

    :param name: name of the action to update
    :param value: new shortcut
    :param text: text of the action (translatable)
    """
    global _MAP
    _MAP[name][_INDEX_VALUE] = shortcut
    _MAP[name][_INDEX_TEXT] = text


def get_all_names():
    """
    Get all action names.

    This function is called by the shortcuts preference page, yo should never
    have to call it yourself.
    """
    global _MAP
    return sorted(_MAP.keys())


def get_all_texts():
    """
    Get all action texts (possibly translated).
    """
    global _MAP
    return sorted([v[_INDEX_TEXT] for v in _MAP.values()])


def restore_defaults():
    """
    Updates every shortcut with its default value.

    This function is called by the shortcuts preference page, yo should never
    have to call it yourself.
    """
    global _MAP
    load()
    for name in get_all_names():
        _MAP[name][_INDEX_VALUE] = _MAP[name][_INDEX_DEFAULT]
    save()


def load():
    """
    Loads the shortcuts map from QSettings.

    This function is called by the application internally, you should never
    have to call it yourself.
    """
    global _MAP
    _MAP = _get_map()


def save():
    """
    Saves the shortcuts map to QSettings

    This function is called by the application when you apply the preferences.
    You should never have to call it yourself
    """
    global _MAP
    _set_map(_MAP)


#: The global shortcuts map instance
_MAP = None
#: Index of the settings value
_INDEX_VALUE = 0
#: Index of the default value
_INDEX_DEFAULT = 1
#: Index text
_INDEX_TEXT = 2


def _get_map():
    string = QtCore.QSettings().value('env/shortcuts', '{}')
    data = json.loads(string)
    if data:
        try:
            k, (name, sh, text) = list(data.items())[0]
        except ValueError:  # pragma: no cover
            data = {}  # old format used
    return data


def _set_map(shortcuts_map):
    QtCore.QSettings().setValue('env/shortcuts', json.dumps(shortcuts_map))
