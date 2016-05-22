# -*- coding: utf-8 -*-
# :Project:   metapensiero.tool.tinject -- Repeat a list of sub-steps
# :Created:   sab 21 mag 2016 14:00:00 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

import inquirer
from . import Step, run_steps


class Repeat(Step):
    def __init__(self, state, config):
        super().__init__(state, config)
        self.description = config.get('description')
        self.answers_name = config.get('answers')
        self.count = config.get('count')
        self.steps = config['steps']
        self.again_message = config.get('again_message', 'Another loop?')

    def announce(self):
        if self.description:
            print("\n%s\n" % self.description)

    def __call__(self, defaults):
        if self.answers_name:
            answers = self.state.answers[self.answers_name] = []
            register_answers = answers.append
        else:
            def register_answers(answers):
                raise RuntimeError('Missing "answers" name in config')

        if self.count:
            for i in range(self.count):
                run_steps(self.state, self.steps, {}, register_answers)
        else:
            while True:
                run_steps(self.state, self.steps, {}, register_answers)
                again = inquirer.prompt([
                    inquirer.Confirm('again', message=self.again_message)])['again']
                if not again:
                    break
