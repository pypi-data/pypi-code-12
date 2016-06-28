"""
This module contains some function to query system settings.

This module is part of the Public API (i.e. backward compatibility should
be kept and this module should have a unit test suite).
"""
import os
import platform
import shutil


#: True on Windows, otherwise False
WINDOWS = platform.system() == 'Windows'
#: True on Linux, otherwise False
LINUX = platform.system() == 'Linux'
#: True on Mac OSX, otherwise False
DARWIN = platform.system() == 'Darwin'

#: True if the application is running on plasma desktop
PLASMA_DESKTOP = 'plasma' in os.environ.get('DESKTOP_SESSION', '')
GNOME_DESKTOP = 'gnome' in os.environ.get('DESKTOP_SESSION', '')
UNITY_DESKTOP = 'ubuntu' in os.environ.get('DESKTOP_SESSION', '') or \
    'unity' in os.environ.get('DESKTOP_SESSION', '')


def get_app_data_directory():
    """
    Gets the platform specific application data directory (
    where we store the log file and and the python backend libraries).

    - GNU/Linux: ``~/.hackedit``
    - OSX: ``~/Library/Application Support/HackEdit``
    - WINDOWS: ``%APPDATA%\HackEdit``

    :return: platform specific data directory.
    """
    def get_path():
        if WINDOWS:
            # todo: this is wrong, need to find the proper path.
            return os.path.join(os.getenv('APPDATA'), 'HackEdit')
        elif DARWIN:
            return os.path.join(
                os.path.expanduser("~"), 'Library', 'Application Support',
                'HackEdit')
        else:
            return os.path.join(os.path.expanduser("~"), '.hackedit')

    retval = get_path()
    try:
        os.makedirs(retval)
    except FileExistsError:
        pass
    return retval


def get_user_workspaces_dir():
    """
    Gets the directory for user workspaces directory.
    """
    return os.path.join(get_app_data_directory(), 'workspaces')


def which(program,  mode=os.F_OK | os.X_OK, path=None):
    """
    Given a command, mode, and a PATH string, return the path which
    conforms to the given mode on the PATH, or None if there is no such
    file.

    `mode` defaults to os.F_OK | os.X_OK. `path` defaults to the result
    of os.environ.get("PATH"), or can be overridden with a custom search
    path.

    :param program: Program to locate
    :return: Path of the program or None if the program could not be found.
    """
    ret = shutil.which(program, mode, path)
    if ret:
        ret = os.path.normpath(ret)
    return ret


def get_authentication_program():
    """
    Gets the authentication program used to run command as root.

    The function try to use one of the following programs:
        - gksu
        - kdesu
        - pseudo on OS X (https://github.com/sstephenson/pseudo)

    """
    if LINUX:
        for program in ['gksu', 'kdesu', 'kdesudo', 'beesu']:
            if which(program) is not None:
                return program
    elif DARWIN:
        return 'pseudo'
    elif WINDOWS:
        return None


def get_cmd_open_folder_in_terminal():
    """
    Gets a cross-platform, format string which contains the command needed for
    opening a folder in a terminal. The format string contains one placeholder
    for the path to open.

    - Windows: ```cmd.exe /K "cd /d "%s"```
    - OSX: ```open -b com.apple.terminal %s```
    - Linux: depends on the installed terminal application:
        - ```konsole --workdir %s```
        - ```gnome-terminal --working-directory %s```
        - ```xfce4-terminal --working-directory %s```
        - (fallback) ```xterm -e "cd %s"```

    .. note:: The user is free to change that command, if you want to use it
        in your plugin, use api.utils.get_cmd_open_folder_in_terminal which
        takes the user's preferences into account.
    """
    if LINUX:
        args = {
            'gnome-terminal': '--working-directory %s',
            'konsole': '--workdir %s',
            'xfce4-terminal': '--working-directory %s',
            'pantheon-terminal': '--working-directory %s'
        }
        for program in ['gnome-terminal', 'xfce4-terminal', 'konsole',
                        'pantheon-terminal']:
            if which(program) is not None:
                return '{0} {1}'.format(program, args[program])
        return 'xterm -e "cd %s"'
    elif WINDOWS:
        return 'cmd.exe /k "cd /d %s"'
    elif DARWIN:
        return 'open -b com.apple.terminal %s'


def get_cmd_run_command_in_terminal(use_hackedit_console=True):
    """
    Gets a cross-platform, format string which contains the command needed for
    running a command in a terminal. The format string contains one placeholder
    for command to run.

    If use_hackedit_console is True, programs will run through the
    ``heconsole`` binary, whose sole purpose is to maintain the terminal open
    after the command terminated.

    .. note:: The user is free to change that command, if you want to use it
        in your plugin, use api.utils.get_cmd_run_command_in_terminal which
        takes the user's preferences into account.
    """
    if LINUX:
        args = {
            'gnome-terminal': '-e %s',
            'konsole': '-e %s',
            'xfce4-terminal': '-e %s',
            'pantheon-terminal': '-e %s'
        }
        cmd = 'xterm -e "%s"'
        for program in ['gnome-terminal', 'xfce4-terminal', 'konsole',
                        'pantheon-terminal']:
            if which(program) is not None:
                cmd = '{0} {1}'.format(program, args[program])
    elif WINDOWS:
        cmd = '%s'
    elif DARWIN:
        cmd = 'open %s'
    if use_hackedit_console:
        cmd = cmd % 'heconsole' + ' %s'
    return cmd
