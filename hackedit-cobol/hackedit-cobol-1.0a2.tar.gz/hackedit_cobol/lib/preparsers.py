import json
import locale
import os
import shlex

from PyQt5 import QtCore
from hackedit import api

from hackedit_cobol.lib.compiler import check_mtime


_ = api.gettext.get_translation(package='hackedit-cobol')


DEFAULT_CONFIG = {
    'name': '',
    'associated-extensions': [],
    'path': '',
    'flags': '',
    'only-preparser': True,
    'output-rule': '$file.cob',
    'extra-cobol-compiler-flags': ''
}


def get_configs():
    """
    Gets the list of compiler configurations.
    """
    configs = json.loads(QtCore.QSettings().value(
        'cobol/preparser_configs', '[]'))
    return sorted(configs, key=lambda x: x['name'])


def set_configs(configs):
    """
    Saves the list of compiler configurations.
    """
    configs = json.dumps(configs)
    QtCore.QSettings().setValue('cobol/preparser_configs', configs)


def get_config(cfg_name):
    """
    Gets the specified compiler config or None if the config name does not
    exist.
    """
    for cfg in get_configs():
        if cfg['name'] == cfg_name:
            return cfg
    return None


def get_preparser_for_file(file_path):
    """
    Gets the preparser for a given source file.

    Returns a Preparser instance if a preparser was found for the file
    extensions, otherwise returns None.
    """
    ext = '*%s' % os.path.splitext(file_path)[1]
    for cfg in get_configs():
        if ext in cfg['associated-extensions']:
            return Preparser(cfg)
    return None


class Preparser:
    """
    Interface to a preparser.
    """
    CRASH_CODE = 139

    def __init__(self, config):
        """
        :param config: Preparser configuration dict.
        """
        self.config = config

    @property
    def only_preparser(self):
        """
        Checks if only preparser must be run, otherwise the COBOL compiler
        will be run after preparser automatically.
        """
        return self.config['only-preparser']

    def get_output_file_path(self, src_path):
        """
        Determines the preparser output file path for a given source file.

        :param src_path: path to the input source file
        """
        if not os.path.isabs(src_path):
            raise ValueError('Input source path must be absolute')
        file_name = self.get_file_name(src_path)
        rule = self.config['output-rule']
        path = rule.replace('$file', file_name)
        if not os.path.isabs(path):
            path = os.path.abspath(os.path.join(
                os.path.dirname(src_path),
                path))
        return path

    @staticmethod
    def get_file_name(src_path):
        """
        Gets the filename (without directories and extension).
        """
        return os.path.splitext(os.path.split(src_path)[1])[0]

    def get_command(self, src_path):
        """
        Gets the command for preparsing ``src_path``.

        Returns the path to the preparser executable and the list of arguments.
        """
        file_name = self.get_file_name(src_path)
        program = self.config['path']
        args = shlex.split(
            self.config['flags'].replace('$file', file_name), posix=False)
        return program, args

    def preparse(self, src_path):
        """
        Executes the preparser process.

        Returns a tuple: command, exit_code, output, output_pth
        """
        pgm, args = self.get_command(src_path)
        working_dir = os.path.dirname(src_path)
        command = '%s %s' % (pgm, ' '.join(args))

        output_pth = self.get_output_file_path(src_path)
        dirname = os.path.dirname(output_pth)

        # check permission
        if not os.access(dirname, os.W_OK):
            raise OSError('PermissionError: build directory is read-only')
        if os.path.exists(output_pth) and not os.access(output_pth, os.W_OK):
            raise OSError('PermissionError: %s is read-only' % output_pth)

        # check if not already preparsed and up to date
        if not check_mtime(src_path, output_pth):
            return command, 0, 'Preparser skipped, up to date...', \
                output_pth

        # run preparser
        process = QtCore.QProcess()
        process.setWorkingDirectory(working_dir)
        process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        process.start(pgm, args)
        process.waitForFinished()

        # determine exit code (and handle crashed processes)
        if process.exitStatus() != process.Crashed:
            exit_code = process.exitCode()
        else:
            exit_code = self.CRASH_CODE

        # read output
        try:
            output = process.readAllStandardOutput().data().decode(
                locale.getpreferredencoding())
        except UnicodeDecodeError:
            output = 'Failed to decode compiler output with encoding %s' % \
                     locale.getpreferredencoding()

        return command, exit_code, output, output_pth
