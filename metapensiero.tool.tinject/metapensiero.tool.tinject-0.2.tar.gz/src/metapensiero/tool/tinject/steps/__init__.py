# -*- coding: utf-8 -*-
# :Project:   metapensiero.tool.tinject -- Steps definitions
# :Created:   gio 21 apr 2016 18:44:56 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

class Step(object):
    def __init__(self, state, config):
        self.state = state

    def announce(self):
        self.state.announce('*', self.__class__.__name__)

    def __call__(self):
        raise NotImplementedError('%s should implement the __call__ method'
                                  % self.__class__.__name__)


def run_steps(state, steps):
    for step in steps:
        items = step.items()
        assert len(items) == 1, "Expected a single item in %r" % step
        for name, details in items:
            pass
        if name not in steps_by_name:
            raise ValueError('Unrecognized step name: %s' % name)
        stepi = steps_by_name[name](state, details)
        stepi.announce()
        if not state.dry_run:
            answers = stepi()
            if answers:
                state.answers.update(answers)


steps_by_name = {}
register_step = steps_by_name.__setitem__


from .changefile import ChangeFile
register_step('changefile', ChangeFile)

from .createdir import CreateDirectory
register_step('createdir', CreateDirectory)

from .createfile import CreateFile
register_step('createfile', CreateFile)

from .prompt import Prompt
register_step('prompt', Prompt)

from .pythonscript import PythonScript
register_step('python', PythonScript)
