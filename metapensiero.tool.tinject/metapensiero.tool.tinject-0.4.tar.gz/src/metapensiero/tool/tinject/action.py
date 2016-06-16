# -*- coding: utf-8 -*-
# :Project:   metapensiero.tool.tinject -- Action implementation
# :Created:   ven 22 apr 2016 09:29:22 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

from .steps import Prompt, run_steps


class Action(object):
    def __init__(self, state, name, details):
        self.state = state
        self.description = details.get('description', name)
        self.prompt = details.get('prompt')
        self.steps = details['steps']

    def __call__(self):
        self.state.announce('=', "%s", self.description)
        if self.prompt:
            prompt = Prompt(self.state, self.prompt)
            self.state.answers.update(prompt(self.state.answers))
        run_steps(self.state, self.steps)
