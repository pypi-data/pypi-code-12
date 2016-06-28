"""
Cobol linter; use open COBOL to check your your syntax on the fly.
"""
import locale
import os
import shlex
import tempfile
import time

from hackedit import api
from hackedit.app import environ
from pyqode.cobol.backend import workers
from pyqode.core.backend import NotRunning
from pyqode.core.modes import CheckerMode
from pyqode.qt import QtCore

import hackedit_cobol.lib.compiler
import hackedit_cobol.lib.preparsers
from hackedit_cobol.lib import compiler, preparsers, utils
from hackedit_cobol.plugins import project_mode, file_mode


_ = api.gettext.get_translation(package='hackedit-cobol')


def make_linter_command(cobol_file_name, original_file_path, config):
    preparser = preparsers.get_preparser_for_file(cobol_file_name)
    args = ['-fsyntax-only', '-I%s' % os.path.dirname(original_file_path)]
    args.append('-std=%s' % config['standard'])
    args += config['extra-compiler-flags']
    original_path = os.path.dirname(original_file_path)
    if workers.free_format:
        args.append('-free')
    copybooks = config['copybook-paths']
    if copybooks:
        for pth in copybooks:
            if not pth:
                continue
            if not os.path.isabs(pth):
                # expand relative path based on the original source path
                # See github issue #119
                pth = os.path.abspath(os.path.join(original_path, pth))
            args.append('-I%s' % pth)

    lib_paths = config['library-paths']
    if lib_paths:
        for pth in lib_paths:
            if pth:
                args.append('-L%s' % pth)
    libs = config['libraries']
    if libs:
        for lib in libs:
            if lib:
                args.append('-l%s' % lib)
    args.append(cobol_file_name)

    if preparser:
        args += shlex.split(preparser.config['extra-cobol-compiler-flags'],
                            posix=False)
    if not preparser:
        ext = os.path.splitext(original_file_path)[1]
        for cfg in hackedit_cobol.lib.preparsers.get_configs():
            for ext_candidate in cfg['associated-extensions']:
                test_path = original_file_path.replace(
                    ext, ext_candidate.replace('*', ''))
                if os.path.exists(test_path):
                    args += shlex.split(cfg['extra-cobol-compiler-flags'],
                                        posix=False)
                    break

    pgm = compiler.GnuCOBOLCompiler(config).get_full_compiler_path()

    if pgm and ' ' in pgm:
        pgm = '"%s"' % pgm

    return pgm, args


def lint(request_data):
    """
    Performs linting of a COBOL document.

    This method will perform on the pyqode backend.

    :param request_data: work request data (dict)
    :return: status, messages
    """
    environ.load()

    code = request_data['code']
    path = request_data['path']

    try:
        prj = request_data['project_path']
    except KeyError:
        # single file mode
        cfg_name = file_mode.get_file_compiler(path)
        compiler_config = hackedit_cobol.lib.compiler.get_compiler_config(
            cfg_name)
        file_cfg = file_mode.get_file_config(path)
        config = file_mode.BuildThread.setup_overrides(
            compiler_config, file_cfg)
    else:
        # project mode
        cfg_name = project_mode.get_project_compiler(prj)
        compiler_config = hackedit_cobol.lib.compiler.get_compiler_config(
            cfg_name)
        prj_config = project_mode.get_project_config(prj)

        rel_fpath = os.path.relpath(path, prj)

        file_config = None
        for file_cfg in prj_config:
            if file_cfg['path'] == rel_fpath:
                file_config = file_cfg
                break
        else:
            file_config = compiler_config
        config = project_mode.BuildThread.setup_overrides(
            compiler_config, file_config)

    ext = '*%s' % os.path.splitext(path)[1]
    if ext not in utils.get_compilable_extensions():
        return []

    # code might not have been saved yet, run cobc on a tmp file
    # we use a time stamp to avoid overwriting the file another cobc
    # instance might be compiling.
    file_name = os.path.split(path)[1]
    file_name, ext = os.path.splitext(file_name)
    tmp_name = '%s.%s%s' % (file_name, str(int(time.time())), ext)
    tmp_pth = os.path.join(tempfile.gettempdir(), tmp_name)
    with open(tmp_pth, 'w') as f:
        f.write(code)

    pgm, args = make_linter_command(tmp_name, path, config)

    process = QtCore.QProcess()
    process.setWorkingDirectory(os.path.dirname(tmp_pth))
    process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
    process.setProcessEnvironment(
        compiler.GnuCOBOLCompiler(config).setup_environment())
    print('linter command: %s %s' % (pgm, ' '.join(args)))
    print('working directory: %s' % process.workingDirectory())
    process.start(pgm, args)
    process.waitForFinished()
    output = process.readAllStandardOutput().data().decode(
        locale.getpreferredencoding())
    print('linter raw output: %s' % output)
    messages = compiler.GnuCOBOLCompiler.parse_output(
        output, process.workingDirectory(), use_dicts=True)
    preparser = preparsers.get_preparser_for_file(tmp_name)
    if preparser:
        to_remove = []
        for msg in messages:
            if 'EXEC' in msg[0]:
                to_remove.append(msg)
        for msg in to_remove:
            messages.remove(msg)
    print('linter parsed output: %r' % messages)
    os.remove(tmp_pth)
    return messages


class CobolLinterMode(CheckerMode):
    def __init__(self):
        super().__init__(lint)

    def _request(self):
        # overriden to include the project path (in order to deduce the
        # compiler config)
        if not self.editor:
            return
        from hackedit_cobol.plugins.project_mode import CobProjectManager
        if api.plugins.get_plugin_instance(CobProjectManager):
            request_data = {
                'code': self.editor.toPlainText(),
                'path': self.editor.file.path,
                'encoding': self.editor.file.encoding,
                'project_path': api.project.get_current_project()
            }
        else:
            request_data = {
                'code': self.editor.toPlainText(),
                'path': self.editor.file.path,
                'encoding': self.editor.file.encoding
            }
        try:
            self.editor.backend.send_request(
                self._worker, request_data, on_receive=self._on_work_finished)
            self._finished = False
        except NotRunning:
            # retry later
            QtCore.QTimer.singleShot(100, self._request)
