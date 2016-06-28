import re
import os
import locale
import fnmatch
import json
import logging

from PyQt5 import QtCore
from hackedit import api
from pyqode.core.cache import Cache


_ = api.gettext.get_translation(package='hackedit-cobol')


#: The list of default compilable extensions
DEFAULT_COMPILABLE_EXTENSIONS = ['*.cbl', '*.cob']


def get_compilable_extensions(include_preparsers=False, include_upper=True):
    """
    Gets the list of compilable extensions (including or excluding the
    preparser extensions).

    Those extensions can be modified by the user (excluding preparser
    extensions)

    :param include_preparsers: True to include preparser extensions. Default
        is False.
    """
    value = json.loads(QtCore.QSettings().value(
        'cobol/compilable_extensions', json.dumps(
            DEFAULT_COMPILABLE_EXTENSIONS)))

    if include_upper:
        for v in value.copy():
            value.append(v.upper())

    if include_preparsers:
        from .preparsers import get_configs

        for cfg in get_configs():
            for ext in cfg['associated-extensions']:
                value.append(ext.upper())
                value.append(ext.lower())

    return sorted(list(set(value)))


def set_compilable_extensions(extensions):
    """
    Sets the compilable extension

    ..note:: make sure to not include preparser extensions!
    """
    assert isinstance(extensions, list)
    QtCore.QSettings().setValue('cobol/compilable_extensions',
                                json.dumps(list(set(extensions))))


def is_compilable(file_path):
    """
    Checks whether a file is compilable or not.
    """
    if file_path:
        for ext in get_compilable_extensions(include_preparsers=True):
            if fnmatch.fnmatch(file_path, ext):
                return True
    return False


def get_compilable_filter():
    """
    Gets a QFileDialog filter that contains all compilable extensions.
    """
    exts = ' '.join(get_compilable_extensions(include_preparsers=True))
    return _('COBOL source (%s)') % exts


def get_file_encoding(filename):
    """
    Gets the encoding for opening file.

    Try to see if there is an encoding in cache for the given filename,
    otherwise try if we can read the file using one of the user defined
    encodings (the one added to the encodings menu). If none worked, we try
    with the system defined encoding.

    :param filename: path of the file.
    :return: encoding
    """
    try:
        encoding = Cache().get_file_encoding(filename)
    except KeyError:
        for encoding in Cache().preferred_encodings:
            try:
                with open(filename, encoding=encoding) as f:
                    f.read()
            except (UnicodeDecodeError, OSError):
                continue
            else:
                _logger().debug('a working encoding was found: %s', encoding)
                return encoding
            encoding = locale.getpreferredencoding()
            _logger().warning(
                'encoding for %s not found in cache, using locale preferred '
                'encoding instead: %s', filename, encoding)
            return encoding
    else:
        _logger().debug('found encoding in cache: %s', encoding)
        return encoding


def get_submodules(filename, recursive=True):
    """
    Gets the list of submodules used by a given program.

    :param filename: path of the file to analyse.
    :param recursive: True to perform recursive analysis (analyses
        submodules of submodules recursively).
    :return: The set of submodules that needs to be compiled to the
        requested program/module.
    """
    encoding = get_file_encoding(filename)
    directory = os.path.dirname(filename)
    submodules = []
    prog = re.compile(r'^[\s\d\w]*CALL[\s\n]*".*".*$',
                      re.MULTILINE | re.IGNORECASE)
    try:
        with open(filename, 'r', encoding=encoding) as f:
            content = f.read()
    except OSError:
        _logger().exception('failed to open cobol source file to get '
                            'submodules')
    for m in prog.findall(content):
        try:
            module_base_name = re.findall('"(.*)"', m)[0]
        except IndexError:
            continue
        # try to see if the module can be found in the current
        # directory
        for ext in get_compilable_extensions(
                include_preparsers=True, include_upper=not api.system.WINDOWS):
            pth = os.path.join(directory, module_base_name +
                               ext.replace('*', ''))
            if os.path.exists(pth) and pth.lower() not in submodules and \
                    filename != pth:
                submodules.append(os.path.normpath(pth))
                if recursive:
                    submodules += get_submodules(pth)

    submodules = list(set(submodules))
    _logger().debug('submodules of %s: %r', filename, submodules)
    return submodules


def _logger():
    return logging.getLogger(__name__)
