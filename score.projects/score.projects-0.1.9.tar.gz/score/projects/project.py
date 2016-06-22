# Copyright © 2015,2016 STRG.AT GmbH, Vienna, Austria
#
# This file is part of the The SCORE Framework.
#
# The SCORE Framework and all its parts are free software: you can redistribute
# them and/or modify them under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation which is in the
# file named COPYING.LESSER.txt.
#
# The SCORE Framework and all its parts are distributed without any WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. For more details see the GNU Lesser General Public
# License.
#
# If you have not received a copy of the GNU Lesser General Public License see
# http://www.gnu.org/licenses/.
#
# The License-Agreement realised between you as Licensee and STRG.AT GmbH as
# Licenser including the issue of its valid conclusion and its pre- and
# post-contractual effects is governed by the laws of Austria. Any disputes
# concerning this License-Agreement including the issue of its valid conclusion
# and its pre- and post-contractual effects are exclusively decided by the
# competent court, in whose district STRG.AT GmbH has its registered seat, at
# the discretion of STRG.AT GmbH also the competent court, in whose district the
# Licensee has his registered seat, an establishment or assets.

import os
from vex.main import _main as vex_main
from score.cli.conf import (
    rootdir, add as addconf, make_default as make_default_conf)
import shutil
import sys


class Project:
    """
    A Project representation, basically consisting of (1) a name, defining the
    projects virtual environment path, and (2) a project folder, where a python
    package is expected (including its setup.py).
    """

    def __init__(self, conf, name, folder):
        self.conf = conf
        self.name = name
        self.folder = folder

    def recreate_venv(self, site_packages=False):
        """
        (Re-)creates this project's virtual environment, deleting the old
        virtualenv folder, if one is found. Afterwards, it will register all
        configuration files (files in the project's root folder, that end on
        '.conf') as configuration files, so that they are available to the score
        CLI inside the virtual environment.
        """
        try:
            shutil.rmtree(self.venvdir)
        except FileNotFoundError:
            pass
        create_args = ['--python', sys.executable, '--make', 'true']
        if site_packages:
            create_args.append('--site-packages')
        self.vex(*create_args)
        self.vex('pip', 'install', '--upgrade', 'pip')
        self.vex('pip', 'install', 'score.cli')
        self.vex('pip', 'install', '--editable', self.folder)
        for file in os.listdir(self.folder):
            if not file.endswith('.conf'):
                continue
            name = file[:-5]
            file = os.path.join(self.folder, file)
            addconf(name, file, venv=self.venvdir)
            make_default_conf(name, venv=self.venvdir)

    def install(self):
        """
        Executes the ``setup.py`` in this project's root folder.
        """
        self.vex('pip', 'install', '--upgrade', 'pip')
        self.vex('pip', 'install', '--editable', self.folder)

    def spawn_shell(self):
        """
        Spawns a shell in this project's root folder.
        """
        self.vex()

    def vex(self, *args):
        """
        Executes a *vex* command in this project's virtualenv. The *args* are
        the command-line arguments to the *vex* command.
        """
        environ = os.environ.copy()
        environ['VIRTUAL_ENV_NAME'] = self.name
        # see https://github.com/sashahart/vex/issues/46
        # and https://github.com/pypa/virtualenv/issues/322
        environ.pop('__PYVENV_LAUNCHER__', None)
        vex_main(environ, ('--path', self.venvdir, '--cwd', self.folder) + args)

    @property
    def venvdir(self):
        return os.path.join(rootdir(global_=True), 'projects', self.name)

    @property
    def exists(self):
        return os.path.exists(self.folder)
