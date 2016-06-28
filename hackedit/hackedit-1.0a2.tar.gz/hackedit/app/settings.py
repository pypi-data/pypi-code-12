"""
Provides a simplified access to the common application settings (not specific
to a plugin).
"""
import locale
import logging
import os

from PyQt5 import QtCore, QtWidgets
from pyqode.core.modes import CodeCompletionMode
from pyqode.core.widgets import FileSystemContextMenu


# load it once, for performance reasons
_SETTINGS = QtCore.QSettings()


DEFAULT_IGNORE_PATTERNS = [
    '.git', '.hg', '.svn', '_svn', '.hackedit', '.tox', '.cache', '*~',
    '*.pyc', '*.pyo', '*.coverage', '.DS_Store', '__pycache__'
]


def load():
    """
    Loads/refreshes settings
    """
    global _SETTINGS
    _SETTINGS = QtCore.QSettings()
    return _SETTINGS


# -----------------------------------------------------------------------------
# Environment settings
# -----------------------------------------------------------------------------
def show_menu():
    return bool(int(_SETTINGS.value('env/show_menu', 0)))


def set_show_menu(value):
    _SETTINGS.setValue('env/show_menu', int(value))


def widescreen_layout():
    """
    True to use a widescreen layout where the left and right dock widget
    takes all the height of the window.
    """
    widescreen = 0
    rec = QtWidgets.qApp.desktop().screenGeometry()
    ratio = rec.width() / rec.height()
    if ratio > 4/3:
        widescreen = 1
    return bool(int(_SETTINGS.value('env/widescreen_layout', widescreen)))


def set_widescreen_layout(value):
    _SETTINGS.setValue('env/widescreen_layout', int(value))


def dark_theme():
    """
    True for dark theme, else native theme.

    :return: bool
    """
    return bool(int(_SETTINGS.value('env/dark', 0)))


def set_dark_theme(value):
    """
    Sets dark theme (True/False)

    :param value: Enable/Disable dark theme.
    :type value: bool
    """
    _SETTINGS.setValue('env/dark', int(value))


def use_system_icons():
    return bool(int(_SETTINGS.value('env/system_icons', 1)))


def set_use_system_icons(val):
    _SETTINGS.setValue('env/system_icons', int(val))


def show_tray_icon():
    return bool(int(_SETTINGS.value('env/show_tray_icon', 0)))


def set_show_tray_icon(value):
    return _SETTINGS.setValue('env/show_tray_icon', int(value))


def icon_theme():
    """
    Gets the icon theme to use.

    :return: hackedit.icons.IconThemes, default is system.
    """
    from hackedit.api import system, utils
    from hackedit.app import icons
    dark = utils.is_dark_theme()
    default_theme = 'Breeze' if not dark else 'Breeze Dark'
    if system.LINUX:
        default_theme = icons.system_icon_theme()
    theme = _SETTINGS.value('env/icons', default_theme)
    return theme


def set_icon_theme(value):
    """
    Sets the icon theme to use
    """
    _SETTINGS.setValue('env/icons', value)


def toolbar_icon_size():
    """
    Gets the toolbar icon size. Default is 22.

    :return: int
    """
    return int(_SETTINGS.value('env/toolbar_icon_size', 22))


def set_toolbar_icon_size(value):
    """
    Sets the toolbar icon size.
    :param value: icon size (int)
    """
    _SETTINGS.setValue('env/toolbar_icon_size', int(value))


def restore_session():
    return bool(int(_SETTINGS.value('env/restore_session', 1)))


def set_restore_session(val):
    _SETTINGS.setValue('env/restore_session', int(val))


def file_manager_cmd():
    try:
        default = FileSystemContextMenu.get_file_explorer_command()
    except Exception:
        default = ''
    return _SETTINGS.value('env/file_manager_command', default)


def set_file_manager_cmd(value):
    try:
        value % '/path/'
    except TypeError:
        value += ' %s'
    _SETTINGS.setValue('env/file_manager_command', value)


def get_cmd_open_folder_in_terminal():
    from hackedit.api import system
    return _SETTINGS.value('env/cmd_open_folder_in_terminal',
                           system.get_cmd_open_folder_in_terminal())


def set_cmd_open_folder_in_terminal(value):
    try:
        value % '/path/'
    except TypeError:
        value += ' %s'
    return _SETTINGS.setValue('env/cmd_open_folder_in_terminal', value)


def get_cmd_run_command_in_terminal():
    from hackedit.api import system
    return _SETTINGS.value('env/cmd_run_command_in_terminal',
                           system.get_cmd_run_command_in_terminal())


def set_cmd_run_command_in_terminal(value):
    try:
        value % '/path/'
    except TypeError:
        value += ' %s'
    return _SETTINGS.setValue('env/cmd_run_command_in_terminal', value)


def use_default_browser():
    from hackedit.api import system
    return bool(int(_SETTINGS.value('env/use_default_browser',
                                    1 if not system.DARWIN else 0)))


def set_use_default_browser(value):
    return _SETTINGS.setValue('env/use_default_browser', int(value))


def get_custom_browser_command():
    from hackedit.api import system
    default = 'firefox %s'
    if system.DARWIN:
        default = 'open -b com.apple.Safari %s'
    ret_val = _SETTINGS.value('env/custom_browser_command', '')
    if not ret_val:
        ret_val = default
    return ret_val


def set_custom_browser_command(value):
    try:
        value % '/path/'
    except TypeError:
        if value:
            value += ' %s'
    return _SETTINGS.setValue('env/custom_browser_command', value)


def show_splashscreen():
    return bool(int(_SETTINGS.value(
        'env/show_splashscreen', 1)))


def set_show_splashscreen(value):
    return _SETTINGS.setValue(
        'env/show_splashscreen', int(value))


def automatically_check_for_updates():
    from hackedit.api import system
    default = True
    if system.LINUX:
        # on linux, package manager should be preferred
        default = False
    return bool(int(_SETTINGS.value(
        'env/automatically_check_for_updates', int(default))))


def set_automatically_check_for_updates(value):
    return _SETTINGS.setValue(
        'env/automatically_check_for_updates', int(value))


def restore_last_window():
    """
    Gets reopen flag: if true the app will automatically reopen the last open
    path
    """
    return bool(int(_SETTINGS.value(
        'env/restore_last_window', 0)))


def set_restore_last_window(value):
    """
    Sets reopen flag: if true the app will automatically reopen the last open
    path
    """
    return _SETTINGS.setValue('env/restore_last_window', int(value))


def confirm_app_exit():
    """
    Gets confirm exit flag: if True a message box will appear to ask you
    if you really want to quit the application, otherwise the application
    will exit without question
    """
    return bool(int(_SETTINGS.value('env/confirm_application_exit', 1)))


def set_confirm_app_exit(value):
    """
    Sets confirm exit flag: if True a message box will appear to ask you
    if you really want to quit the application, otherwise the application
    will exit without question
    """
    return _SETTINGS.setValue('env/confirm_application_exit', int(value))


class OpenMode:
    """
    Enumerates the possible open modes
    """
    #: Always open path in a new window (no multiple project support)
    NEW_WINDOW = 0
    #: Always open path in current window (add to open projects)
    CURRENT_WINDOW = 1
    #: Always ask what do (default).
    ASK_EACH_TIME = 2


def open_mode():
    """
    Gets the path open mode. Default is to always ask.
    """
    return int(_SETTINGS.value(
        'env/open_mode', OpenMode.ASK_EACH_TIME))


def set_open_mode(value):
    """
    Sets the path open mode.
    """
    return _SETTINGS.setValue('env/open_mode', int(value))


def ignored_patterns():
    """
    Gets the list of ignored files and directories
    """
    return _SETTINGS.value(
        'env/ignored_patterns', ';'.join(DEFAULT_IGNORE_PATTERNS)).split(';')


def set_ignored_patterns(val):
    """
    Sets the list of ignored directories
    """
    return _SETTINGS.setValue('env/ignored_patterns', ';'.join(val))


def show_notification_in_sytem_tray():
    return bool(int(_SETTINGS.value(
        'env/show_notification_in_sytem_tray', 1)))


def set_show_notification_in_sytem_tray(val):
    _SETTINGS.setValue('env/show_notification_in_sytem_tray', int(val))


def auto_open_info_notification():
    return bool(int(_SETTINGS.value(
        'env/auto_open_info_notification', 0)))


def set_auto_open_info_notification(val):
    _SETTINGS.setValue('env/auto_open_info_notification', int(val))


def auto_open_warning_notification():
    return bool(int(_SETTINGS.value(
        'env/auto_open_warning_notification', 1)))


def set_auto_open_warning_notification(val):
    _SETTINGS.setValue('env/auto_open_warning_notification', int(val))


def auto_open_error_notification():
    return bool(int(_SETTINGS.value(
        'env/auto_open_error_notification', 1)))


def set_auto_open_error_notification(val):
    _SETTINGS.setValue('env/auto_open_error_notification', int(val))


def log_level():
    return int(_SETTINGS.value('env/log_level', logging.INFO))


def set_log_level(value):
    _SETTINGS.setValue('env/log_level', value)


def indexing_enabled():
    return bool(int(_SETTINGS.value('env/indexing_enabled', 1)))


def set_indexing_enabled(value):
    _SETTINGS.setValue('env/indexing_enabled', int(value))


# -----------------------------------------------------------------------------
# Editor settings
# -----------------------------------------------------------------------------
def margin_position():
    return int(_SETTINGS.value('editor/margin_position', 119))


def set_margin_position(val):
    _SETTINGS.setValue('editor/margin_position', val)


def tab_length():
    return int(_SETTINGS.value('editor/tab_length', 4))


def set_tab_length(val):
    _SETTINGS.setValue('editor/tab_length', val)


def use_spaces_instead_of_tabs():
    return bool(int(_SETTINGS.value('editor/use_spaces', 1)))


def set_use_spaces_instead_of_tabs(val):
    return _SETTINGS.setValue('editor/use_spaces', int(val))


def center_on_scroll():
    return bool(int(_SETTINGS.value('editor/center_on_scroll', 1)))


def set_center_on_scroll(val):
    return _SETTINGS.setValue('editor/center_on_scroll', int(val))


def highlight_caret_scope():
    return bool(int(_SETTINGS.value('editor/highlight_caret_scope', 0)))


def set_highlight_caret_scope(val):
    return _SETTINGS.setValue('editor/highlight_caret_scope', int(val))


def highlight_caret_line():
    return bool(int(_SETTINGS.value('editor/highlight_caret_line', 1)))


def set_highlight_caret_line(val):
    return _SETTINGS.setValue('editor/highlight_caret_line', int(val))


def highlight_parentheses():
    return bool(int(_SETTINGS.value('editor/highlight_parentheses', 1)))


def set_highlight_parentheses(val):
    return _SETTINGS.setValue('editor/highlight_parentheses', int(val))


def convert_tabs():
    return bool(int(_SETTINGS.value('editor/convert_tabs', 1)))


def set_convert_tabs(val):
    return _SETTINGS.setValue('editor/convert_tabs', int(val))


def clean_trailing_whitespaces():
    return bool(int(_SETTINGS.value(
        'editor/clean_trailing_whitespaces', 1)))


def set_clean_trailing_whitespaces(val):
    return _SETTINGS.setValue('editor/clean_trailing_whitespaces', int(val))


def restore_cursor():
    return bool(int(_SETTINGS.value('editor/restore_cursor', 1)))


def set_restore_cursor(val):
    return _SETTINGS.setValue('editor/restore_cursor', int(val))


def safe_save():
    return bool(int(_SETTINGS.value('editor/safe_save', 1)))


def set_safe_save(val):
    return _SETTINGS.setValue('editor/safe_save', int(val))


def default_encoding():
    return _SETTINGS.value('editor/default_encoding',
                           locale.getpreferredencoding())


def set_default_encoding(value):
    return _SETTINGS.setValue('editor/default_encoding', value)


def eol_convention():
    from pyqode.core.managers.file import FileManager
    return int(_SETTINGS.value('editor/eol_convention',
                               FileManager.EOL.System))


def set_eol_convention(val):
    return _SETTINGS.setValue('editor/eol_convention', int(val))


def autodetect_eol():
    return bool(int(_SETTINGS.value('editor/autodetect_eol', 1)))


def set_autodetect_eol(val):
    return _SETTINGS.setValue('editor/autodetect_eol', int(val))


def cc_trigger_len():
    return int(_SETTINGS.value('editor/cc_trigger_len', 0))


def set_cc_trigger_len(val):
    return _SETTINGS.setValue('editor/cc_trigger_len', int(val))


def cc_filter_mode():
    return int(_SETTINGS.value('editor/cc_filter_mode', CodeCompletionMode.FILTER_FUZZY))


def set_cc_filter_mode(val):
    return _SETTINGS.setValue('editor/cc_filter_mode', int(val))


def cc_show_tooltips():
    return bool(int(_SETTINGS.value('editor/cc_show_tooltips', 0)))


def set_cc_show_tooltips(val):
    return _SETTINGS.setValue('editor/cc_show_tooltips', int(val))


def cc_case_sensitive():
    return bool(int(_SETTINGS.value('editor/cc_case_sensitive', 1)))


def set_cc_case_sensitive(val):
    return _SETTINGS.setValue('editor/cc_case_sensitive', int(val))


def show_line_numbers_panel():
    return bool(int(_SETTINGS.value(
        'editor/show_line_numberspanel', 1)))


def set_show_line_numbers_panel(val):
    return _SETTINGS.setValue('editor/show_line_numberspanel', int(val))


def show_folding_panel():
    return bool(int(_SETTINGS.value('editor/show_folding_panel', 1)))


def set_show_folding_panel(val):
    return _SETTINGS.setValue('editor/show_folding_panel', int(val))


def show_errors_panel():
    return bool(int(_SETTINGS.value('editor/show_errors_panel', 1)))


def set_show_errors_panel(val):
    return _SETTINGS.setValue('editor/show_errors_panel', int(val))


def show_global_panel():
    return bool(int(_SETTINGS.value('editor/show_global_panel', 1)))


def set_show_global_panel(val):
    return _SETTINGS.setValue('editor/show_global_panel', int(val))


def text_wrapping():
    return bool(int(_SETTINGS.value('editor/text_wrapping', 0)))


def set_text_wrapping(val):
    _SETTINGS.setValue('editor/text_wrapping', int(val))


def right_margin():
    return bool(int(_SETTINGS.value('editor/right_margin', 1)))


def set_right_margin(val):
    _SETTINGS.setValue('editor/right_margin', int(val))


def auto_indent():
    return bool(int(_SETTINGS.value('editor/auto_indent', 1)))


def set_auto_indent(val):
    _SETTINGS.setValue('editor/auto_indent', int(val))


def auto_complete():
    return bool(int(_SETTINGS.value('editor/auto_complete', 1)))


def set_auto_complete(val):
    _SETTINGS.setValue('editor/auto_complete', int(val))


def backspace_unindents():
    return bool(int(_SETTINGS.value('editor/backspace_unindents', 1)))


def set_backspace_unindents(val):
    return _SETTINGS.setValue('editor/backspace_unindents', int(val))


def color_scheme():
    """
    Gets the color scheme to use.

    The color scheme defines the color of the editor widgets and the Python console.

    :return: Color scheme name.
    """
    from hackedit.api.utils import is_dark_theme
    dark = is_dark_theme()
    return _SETTINGS.value(
        'editor/color_scheme', 'aube' if not dark else 'crepuscule')


def set_color_scheme(value):
    """
    Sets the color scheme to use.

    :param value: color scheme name.
    """
    _SETTINGS.setValue('editor/color_scheme', str(value))


def is_dark_color_scheme(scheme=None):
    if scheme is None:
        scheme = color_scheme()
    return scheme in [
        'darcula', 'fruity', 'native', 'monokai', 'vim', 'paraiso-dark',
        'crepuscule', 'ark-dark', 'midna-dark']


def editor_font():
    """
    Gets the editor font
    """
    return _SETTINGS.value('editor/font', 'Hack')


def set_editor_font(font_name):
    """
    Sets the editor font
    """
    assert isinstance(font_name, str)
    _SETTINGS.setValue('editor/font', font_name)


def editor_font_size():
    """
    Gets the editor font size
    """
    return int(_SETTINGS.value('editor/font_size', 10))


def set_editor_font_size(value):
    """
    Sets the editor font size
    """
    return _SETTINGS.setValue('editor/font_size', value)


def show_whitespaces():
    """
    Gets editor show whitespace flag
    """
    return bool(int(_SETTINGS.value('editor/show_whitespaces', 0)))


def set_show_whitespaces(value):
    """
    Sets editor show whitespaces flag
    """
    return _SETTINGS.setValue('editor/show_whitespaces', int(value))


# -----------------------------------------------------------------------------
# Cached data
# -----------------------------------------------------------------------------
def last_open_dir():
    """
    Gets the last directory used for opening file/directory
    """
    return _SETTINGS.value('_cache/last_open_dir', os.path.expanduser('~'))


def set_last_open_dir(value):
    """
    Sets the directory used by the last call to QFileDialog.
    """
    _SETTINGS.setValue('_cache/last_open_dir', value)
