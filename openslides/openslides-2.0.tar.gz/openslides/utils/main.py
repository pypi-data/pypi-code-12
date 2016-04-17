import argparse
import ctypes
import os
import sys
import tempfile
import threading
import time
import webbrowser

from django.conf import ENVIRONMENT_VARIABLE
from django.core.exceptions import ImproperlyConfigured
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext as _
from django.utils.translation import activate, check_for_language, get_language

DEVELOPMENT_VERSION = 'Development Version'
UNIX_VERSION = 'Unix Version'
WINDOWS_VERSION = 'Windows Version'
WINDOWS_PORTABLE_VERSION = 'Windows Portable Version'


class PortableDirNotWritable(Exception):
    pass


class PortIsBlockedError(Exception):
    pass


class DatabaseInSettingsError(Exception):
    pass


class UnknownCommand(Exception):
    pass


class ExceptionArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise UnknownCommand(message)


def detect_openslides_type():
    """
    Returns the type of this OpenSlides version.
    """
    if sys.platform == 'win32':
        if os.path.basename(sys.executable).lower() == 'openslides.exe':
            # Note: sys.executable is the path of the *interpreter*
            #       the portable version embeds python so it *is* the interpreter.
            #       The wrappers generated by pip and co. will spawn the usual
            #       python(w).exe, so there is no danger of mistaking them
            #       for the portable even though they may also be called
            #       openslides.exe
            openslides_type = WINDOWS_PORTABLE_VERSION
        else:
            openslides_type = WINDOWS_VERSION
    else:
        openslides_type = UNIX_VERSION
    return openslides_type


def get_default_settings_path(openslides_type=None):
    """
    Returns the default settings path according to the OpenSlides type.

    The argument 'openslides_type' has to be one of the three types mentioned in
    openslides.utils.main.
    """
    if openslides_type is None:
        openslides_type = detect_openslides_type()

    if openslides_type == UNIX_VERSION:
        parent_directory = os.environ.get(
            'XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
    elif openslides_type == WINDOWS_VERSION:
        parent_directory = get_win32_app_data_path()
    elif openslides_type == WINDOWS_PORTABLE_VERSION:
        parent_directory = get_win32_portable_path()
    else:
        raise TypeError('%s is not a valid OpenSlides type.' % openslides_type)
    return os.path.join(parent_directory, 'openslides', 'settings.py')


def get_local_settings_path():
    """
    Returns the path to a local settings.

    On Unix systems: 'personal_data/var/settings.py'
    """
    return os.path.join('personal_data', 'var', 'settings.py')


def setup_django_settings_module(settings_path=None, local_installation=None):
    """
    Sets the environment variable ENVIRONMENT_VARIABLE, that means
    'DJANGO_SETTINGS_MODULE', to the given settings.

    If no settings_path is given and the environment variable is already set,
    then this function does nothing.

    If the argument settings_path is set, then the environment variable is
    always overwritten.
    """
    if settings_path is None and os.environ.get(ENVIRONMENT_VARIABLE, None):
        return

    if settings_path is None:
        if local_installation:
            settings_path = get_local_settings_path()
        else:
            settings_path = get_default_settings_path()

    settings_file = os.path.basename(settings_path)
    settings_module_name = ".".join(settings_file.split('.')[:-1])
    if '.' in settings_module_name:
        raise ImproperlyConfigured("'.' is not an allowed character in the settings-file")

    # Change the python path. Also set the environment variable python path, so
    # change of the python path also works after a reload
    settings_module_dir = os.path.abspath(os.path.dirname(settings_path))
    sys.path.insert(0, settings_module_dir)
    try:
        os.environ['PYTHONPATH'] = os.pathsep.join((settings_module_dir, os.environ['PYTHONPATH']))
    except KeyError:
        # The environment variable is empty
        os.environ['PYTHONPATH'] = settings_module_dir

    # Set the environment variable to the settings module
    os.environ[ENVIRONMENT_VARIABLE] = settings_module_name


def get_default_settings_context(user_data_path=None):
    """
    Returns the default context values for the settings template:
    'openslides_user_data_path', 'import_function' and 'debug'.

    The argument 'user_data_path' is a given path for user specific data or None.
    """
    # Setup path for user specific data (SQLite3 database, media, search index, ...):
    # Take it either from command line or get default path
    default_context = {}
    if user_data_path:
        default_context['openslides_user_data_path'] = repr(user_data_path)
        default_context['import_function'] = ''
    else:
        openslides_type = detect_openslides_type()
        if openslides_type == WINDOWS_PORTABLE_VERSION:
            default_context['openslides_user_data_path'] = 'get_win32_portable_user_data_path()'
            default_context['import_function'] = 'from openslides.utils.main import get_win32_portable_user_data_path'
        else:
            path = get_default_user_data_path(openslides_type)
            default_context['openslides_user_data_path'] = repr(os.path.join(path, 'openslides'))
            default_context['import_function'] = ''
    default_context['debug'] = 'False'
    return default_context


def get_default_user_data_path(openslides_type):
    """
    Returns the default path for user specific data according to the OpenSlides
    type.

    The argument 'openslides_type' has to be one of the three types mentioned
    in openslides.utils.main.
    """
    if openslides_type == UNIX_VERSION:
        default_user_data_path = os.environ.get(
            'XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
    elif openslides_type == WINDOWS_VERSION:
        default_user_data_path = get_win32_app_data_path()
    elif openslides_type == WINDOWS_PORTABLE_VERSION:
        default_user_data_path = get_win32_portable_path()
    else:
        raise TypeError('%s is not a valid OpenSlides type.' % openslides_type)
    return default_user_data_path


def get_win32_app_data_path():
    """
    Returns the path to Windows' AppData directory.
    """
    shell32 = ctypes.WinDLL("shell32.dll")
    SHGetFolderPath = shell32.SHGetFolderPathW
    SHGetFolderPath.argtypes = (
        ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32,
        ctypes.c_wchar_p)
    SHGetFolderPath.restype = ctypes.c_uint32

    CSIDL_LOCAL_APPDATA = 0x001c
    MAX_PATH = 260

    buf = ctypes.create_unicode_buffer(MAX_PATH)
    res = SHGetFolderPath(0, CSIDL_LOCAL_APPDATA, 0, 0, buf)
    if res != 0:
        # TODO: Write other exception
        raise Exception("Could not determine Windows' APPDATA path")

    return buf.value


def get_win32_portable_path():
    """
    Returns the path to the Windows portable version.
    """
    # NOTE: sys.executable will be the path to openslides.exe
    #       since it is essentially a small wrapper that embeds the
    #       python interpreter
    portable_path = os.path.dirname(os.path.abspath(sys.executable))
    try:
        fd, test_file = tempfile.mkstemp(dir=portable_path)
    except OSError:
        raise PortableDirNotWritable(
            'Portable directory is not writeable. '
            'Please choose another directory for settings and data files.')
    else:
        os.close(fd)
        os.unlink(test_file)
    return portable_path


def get_win32_portable_user_data_path():
    """
    Returns the user data path to the Windows portable version.
    """
    return os.path.join(get_win32_portable_path(), 'openslides')


def write_settings(settings_path=None, template=None, **context):
    """
    Creates the settings file at the given path using the given values for the
    file template.

    Retuns the path to the created settings.
    """
    if settings_path is None:
        settings_path = get_default_settings_path()

    if template is None:
        with open(os.path.join(os.path.dirname(__file__), 'settings.py.tpl')) as template_file:
            template = template_file.read()

    # Create a random SECRET_KEY to put it in the settings.
    # from django.core.management.commands.startproject
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    context.setdefault('secret_key', get_random_string(50, chars))
    for key, value in get_default_settings_context().items():
        context.setdefault(key, value)

    content = template % context
    settings_module = os.path.realpath(os.path.dirname(settings_path))
    if not os.path.exists(settings_module):
        os.makedirs(settings_module)
    with open(settings_path, 'w') as settings_file:
        settings_file.write(content)
    return os.path.realpath(settings_path)


def start_browser(browser_url):
    """
    Launches the default web browser at the given url and opens the
    webinterface.
    """
    browser = webbrowser.get()

    def function():
        # TODO: Use a nonblocking sleep event here. Tornado has such features.
        time.sleep(1)
        browser.open(browser_url)

    thread = threading.Thread(target=function)
    thread.start()


def get_database_path_from_settings():
    """
    Retrieves the database path out of the settings file. Returns None,
    if it is not a SQLite3 database.

    Needed for the backupdb command.
    """
    from django.conf import settings as django_settings
    from django.db import DEFAULT_DB_ALIAS

    db_settings = django_settings.DATABASES
    default = db_settings.get(DEFAULT_DB_ALIAS)
    if not default:
        raise DatabaseInSettingsError("Default databases is not configured")
    database_path = default.get('NAME')
    if not database_path:
        raise DatabaseInSettingsError('No path or name specified for default database.')
    if default.get('ENGINE') != 'django.db.backends.sqlite3':
        database_path = None
    return database_path


def translate_customizable_strings(language_code):
    """
    Translates all translatable config values and saves them into database.
    """
    if check_for_language(language_code):
        from openslides.core.config import config
        current_language = get_language()
        activate(language_code)
        for name in config.get_all_translatable():
            config[name] = _(config[name])
        activate(current_language)


def is_local_installation():
    """
    Returns True if the command is called for a local installation

    This is the case if manage.py is used, or when the --local-installation flag is set.
    """
    return True if '--local-installation' in sys.argv or 'manage.py' in sys.argv[0] else False
