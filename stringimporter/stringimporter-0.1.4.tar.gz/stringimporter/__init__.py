"""
stringimporter
=================

dumb loading of arbitrary strings into simulated Python modules
"""

import importlib.abc
import sys
import types


class DummyModuleLoader(importlib.abc.SourceLoader):
    def __init__(self, name, src_code, filename=None):
        self._dummy_name = name
        self._src_code = src_code
        if not filename:
            filename = '{}.py'.format(self._dummy_name.replace('.', '/'))
        self._filename = filename

    def get_filename(self, path):
        return self._filename

    def get_data(self, path):
        return self._src_code.encode('utf-8')

    def create_module(self, spec):
        mod = types.ModuleType(self._dummy_name)
        mod.__file__ = self._filename
        sys.modules[mod.__name__] = mod
        return mod


def import_str(module_name, python_code, filename=None, exec_module=True):
    """
    Creates a Python module from a string containing code

    :param str module_name: apparent name of the created module
    :param str python_code: the Python code
    :param bool exec_module: if True (default), imported code will be executed.
        else, you'll have to run loader.exec_module(module)
    :param str filename: we emulate loading from a file,
        you can specify the name here.
    :return: tuple of module loader and module
    """
    loader = DummyModuleLoader(module_name, python_code, filename=filename)
    module = loader.create_module(None)
    if exec_module:
        loader.exec_module(module)
    return loader, module
