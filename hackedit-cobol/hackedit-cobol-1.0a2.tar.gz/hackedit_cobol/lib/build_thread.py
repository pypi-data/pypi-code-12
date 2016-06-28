import logging
import os
import shlex
import traceback

from PyQt5 import QtCore

from hackedit_cobol.lib import utils
from hackedit_cobol.lib.compiler import MODULE


class BuildThreadBase(QtCore.QThread):
    #: signal emitted with the name of the configuration to will be used
    #: to compile the project/file.
    configuration_message = QtCore.pyqtSignal(str)

    #: signal emitted if a secondary compiler config is skipped
    configuration_skipped = QtCore.pyqtSignal(str)

    #: signal emitted when a compilation command has finished.
    #: Parameters:
    #:     - command
    #:     - input file path
    #:     - exit code
    #:     - process output
    command_finished = QtCore.pyqtSignal(str, str, int, str)

    #: Signal emitted if an exception occured (e.g. permission error,...)
    errored = QtCore.pyqtSignal(str, Exception, str)

    #: Signal emitted when the project build has finished.
    finished = QtCore.pyqtSignal(bool)

    def run(self):
        try:
            self.build()
        except Exception as e:
            _logger().exception('exception while running build')
            self.errored.emit('', e, traceback.format_exc())
            self.finished.emit(False)

    def preparse(self, cfg, preparser, abs_path):
        success = True
        try:
            ret_val = preparser.preparse(abs_path)
        except OSError as e:
            _logger().exception('exception occured while preparsing')
            path = cfg['path']
            self.errored.emit(path, e, traceback.format_exc())
            success = False
        else:
            cmd, status, output, _ = ret_val
            self.command_finished.emit(cmd, abs_path, status, output)
            if status != 0:
                success = False
        return success

    def compile(self, cfg, compiler, abs_path, prj_path):
        executable = cfg['filetype'] != MODULE
        success = True
        outdir = None
        if prj_path:
            dirname = os.path.dirname(os.path.relpath(abs_path, prj_path))
            if dirname:
                outdir = os.path.join(
                    prj_path, compiler.config['output-directory'], dirname)

        try:
            ret_val = compiler.compile_file(
                abs_path, executable=executable, out_dir=outdir)
        except OSError as e:
            _logger().exception('exception occured while compiling')
            path = cfg['path']
            self.errored.emit(path, e, traceback.format_exc())
            success = False
        else:
            cmd, status, output, _ = ret_val
            self.command_finished.emit(cmd, abs_path, status, output)
            if status != 0:
                success = False

        try:
            compile_submodules = cfg['compile-submodules']
        except KeyError:
            _logger().debug('no submodules to compile in config: %r', cfg)
        else:
            if compile_submodules:
                submodules = utils.get_submodules(abs_path, recursive=False)
                for path in submodules:
                    sub_cfg = cfg.copy()
                    sub_cfg['filetype'] = compiler.get_file_type(path)
                    sub_cfg['path'] = path
                    self.compile(sub_cfg, compiler, path, prj_path)

        return success

    @staticmethod
    def setup_overrides(compiler_config, cfg, preparser=None):
        try:
            override = cfg['override']
        except KeyError:
            _logger().debug('no settings to override for config: %r', cfg)
        else:
            compiler_config['-static'] = override['-static']
            compiler_config['-debug'] = override['-debug']
            compiler_config['-g'] = override['-g']
            compiler_config['-ftrace'] = override['-ftrace']
            compiler_config['-ftraceall'] = override['-ftraceall']
            compiler_config['-fdebugging-line'] = \
                override['-fdebugging-line']
            compiler_config['extra-compiler-flags'] = \
                override['extra-compiler-flags']
            compiler_config['copybook-paths'] = override['copybook-paths']
            compiler_config['library-paths'] = override['library-paths']
            compiler_config['libraries'] = override['libraries']
        finally:
            compiler_config['free-format'] = cfg['free-format']
            compiler_config['standard'] = cfg['standard']
        if preparser:
            compiler_config['additional-flags'] = \
                shlex.split(preparser.config['extra-cobol-compiler-flags'],
                            posix=False)
        return compiler_config


def _logger():
    return logging.getLogger(__name__)
