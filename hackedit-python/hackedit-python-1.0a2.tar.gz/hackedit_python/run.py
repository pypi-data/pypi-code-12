"""
This module contains the python runner plugin that let you run some
python scripts.
"""
import os

from hackedit import api
from hackedit.api.interpreters import ScriptRunnerPlugin

from .editor import PyCodeEdit
from .interpreters import PythonManager


class PyRun(ScriptRunnerPlugin):
    """
    Plugin for running python scripts.
    """
    def __init__(self, window):
        super().__init__(window, PythonManager())

    def configure(self):
        super().configure()
        # this is very python specific, you should not have to do that for
        # other interpreters.
        self._update_backends()

    def _update_backends(self):
        for editor in api.editor.get_all_editors(include_clones=True):
            if isinstance(editor, PyCodeEdit):
                interpreter = self._get_backend_interpreter(editor.file.path)
                if interpreter and interpreter != editor.backend.interpreter:
                    editor.BACKEND_INTERPRETER = interpreter
                    editor.restart_backend()

    def _get_backend_interpreter(self, path):
        for prj in api.project.get_projects():
            prj = prj + os.sep
            if prj in path:
                return self.interpreter_manager.get_project_interpreter(prj)
        return None
