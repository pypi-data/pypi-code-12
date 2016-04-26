# -*- coding: utf-8 -*-
# :Project:   metapensiero.tool.tinject -- Implementation of createdir step
# :Created:   ven 22 apr 2016 19:48:24 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

from pathlib import Path

from . import Step


class CreateDirectory(Step):
    def __init__(self, state, config):
        super().__init__(state, config)
        self.directory = Path(state.render_string(config['directory']))

    def announce(self):
        self.state.announce('*', "Create directory %s", self.directory)

    def __call__(self):
        if not self.directory.is_dir() and not self.state.dry_run:
            self.directory.mkdir(parents=True)
