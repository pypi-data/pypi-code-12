# -*- coding: utf-8 -*-
# :Project:   metapensiero.tool.tinject -- Implementation of python step
# :Created:   dom 24 apr 2016 23:37:33 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

from pathlib import Path

from . import Step, register_step


class PythonScript(Step):
    def __init__(self, state, config):
        super().__init__(state, config)
        self.script = config['script']

    def announce(self):
        self.state.announce('*', "Execute Python script")

    def __call__(self):
        context = dict(Step=Step, register_step=register_step, state=self.state)
        code = compile(self.script, self.state.configfile, 'exec')
        exec(code, context)
        
