# coding: utf-8
"""Provides convenience functions for nbextension installation."""

from __future__ import (
    absolute_import, division, print_function, unicode_literals,
)

import os

from jupyter_core.application import JupyterApp
from notebook import version_info as notebook_version_info
from notebook.nbextensions import InstallNBExtensionApp

from . import __version__
from . import _jupyter_nbextension_paths
from . import __file__ as nbext_path_src

nbext_path_root = os.path.dirname(nbext_path_src)
nbext_paths = [
    os.path.normpath(os.path.join(nbext_path_root, nbext_pathobj['src'])
    for nbext_pathobj in _jupyter_nbextension_paths()
]

class BaseApp(JupyterApp):
    """Base class for apps."""
    version = __version__

    _log_formatter_cls = LogFormatter

    def _log_format_default(self):
        """A default format for messages."""
        return '%(message)s'

    def migrate_config(self):
        """Override to suppress Jupyter's default migration."""
        pass


class InstallApp(InstallNBExtensionApp, BaseApp):
    name = 'jupyter_highlight_selected_word install'

    def start(self):
        """Override to fix extra_args."""
        if self.extra_args:
           self.log.error('{} takes no positional arguments'.format(self.name))
           self.exit(1)

        for nbext_path in nbext_paths:
            self.extra_args = [nbext_path]
            InstallNBExtensionApp.start(self)


class EnableApp(EnableNBExtensionApp, BaseApp):
    name = 'jupyter_highlight_selected_word enable'

    def start(self):
        """Override to fix extra_args."""
        if self.extra_args:
           self.log.error('{} takes no positional arguments'.format(self.name))
           self.exit(1)

        for nbext_path in nbext_paths:
            self.extra_args = [nbext_path]
            EnableNBExtensionApp.start(self)

        EnableNBExtensionApp.start(self)

for nbext_pathobj in _jupyter_nbextension_paths():
    print(os.path.normpath(os.path.join(nbext_path_root, nbext_pathobj['src']))

self.extra_args

print(nbext_src_path)
